import xml.etree.ElementTree as ET
import os
import sys
import shutil
try:
    from Tkinter import *
except ImportError:
    from tkinter import *
try:
	#Python 2.x
	from tkFileDialog import askopenfilename
	import tkMessageBox
except ImportError:
	#Python 3
	from tkinter.filedialog import askopenfilename
	from tkinter import messagebox as tkMessageBox
	
import ctypes
ctypes.windll.user32.ShowWindow( ctypes.windll.kernel32.GetConsoleWindow(), 6 )

def main(src, des):
	src_path = os.path.dirname(src)
	des_path = os.path.dirname(des)
	mergedProj = os.getcwd() + '\\mergedProj'

	ET.register_namespace('fusion_portal',"http://fusion_portal/1.0") #some name
	ET.register_namespace('xmi', "http://www.omg.org/XMI")
	desSiDic = {}
	desWinAppDic = {}

	def getPortalFile(prjPath):
		for portal_file in os.listdir(prjPath):
			if portal_file.endswith(".fusion_portal"):
				break
		return portal_file
		
	#get source root
	src_portal_file = getPortalFile(src_path)
	src_tree = ET.parse(src_path + '\\' + src_portal_file)
	src_root = src_tree.getroot()

	#get Destination root
	des_portal_file = getPortalFile(des_path)
	des_tree = ET.parse(des_path + '\\' + des_portal_file)
	des_root = des_tree.getroot()

	def mergePortalWorkflowsElm():
		#merge subflows
		des_tree = ET.parse(mergedProj + '\\' + des_portal_file)
		des_root = des_tree.getroot()
		subflows_root = des_root.find("./Workflows")
		desSf = {}
		for sf in des_root.findall("./Workflows/FusionWorkflow"):
			desSf[sf.get('WorkflowName')] = '1'
			
		for x in desSf:
			print(x + ": " +desSf.get(x))
			
		for src_sf in src_root.iter('FusionWorkflow'):
			print('wf ' + src_sf.get('WorkflowName') + ': is appended')
			#continue if destination is having subflow with same name
			if desSf.get(src_sf.get('WorkflowName')) == '1':
				print('workflow with same name exist' + src_sf.get('WorkflowName'))
				sys.exit()
			srcProj = src_portal_file.replace('.fusion_portal', '')
			desProj = des_portal_file.replace('.fusion_portal', '')
			srcWfDigUri = src_sf.get('WorkflowDiagramURI').replace(srcProj, desProj, 1)
			src_sf.set('WorkflowDiagramURI', srcWfDigUri)
			subflows_root.append(src_sf)

		desSf.clear()		
		des_tree.write(open(mergedProj + '\\' + des_portal_file, 'wb'), encoding='UTF-8', xml_declaration=True, default_namespace=None, method="xml")				
		#print 'merged portal is :' + mergedProj + '\\' + des_portal_file

			
	def mergePortalSubflowsElm():
		#merge subflows
		des_tree = ET.parse(mergedProj + '\\' + des_portal_file)
		des_root = des_tree.getroot()
		subflows_root = des_root.find("./Subflows")
		desSf = {}
		for sf in des_root.findall("./Subflows/Subflow"):
			desSf[sf.get('WorkflowName')] = '1'
			
		for x in desSf:
			print(x + ": " +desSf.get(x))
			
		for src_sf in src_root.iter('Subflow'):
			print("wf :" + src_sf.get('WorkflowName') + ': is appended')
			#continue if destination is having subflow with same name
			if desSf.get(src_sf.get('WorkflowName')) == '1':
				continue
			srcProj = src_portal_file.replace('.fusion_portal', '')
			desProj = des_portal_file.replace('.fusion_portal', '')
			srcWfDigUri = src_sf.get('WorkflowDiagramURI').replace(srcProj, desProj, 1)
			src_sf.set('WorkflowDiagramURI', srcWfDigUri)
			subflows_root.append(src_sf)

		desSf.clear()		
		des_tree.write(open(mergedProj + '\\' + des_portal_file, 'wb'), encoding='UTF-8', xml_declaration=True, default_namespace=None, method="xml")				
		
	def replaceScreenID_screen(oldValue, newValue, desAttr, key, keyArrt):
		registerWfNameSpace()
		wfDirPath =  mergedProj + "\\workflows"
		for wf_file in os.listdir(wfDirPath):
			if wf_file.endswith(".fusionworkflow"):
				wf_tree = ET.parse(wfDirPath+"\\" + wf_file)			
				for elem in wf_tree.getiterator():
					if elem.get(keyArrt) is not None and elem.get(desAttr) is not None and key in elem.get(keyArrt):
						elem.set(desAttr, elem.get(desAttr).replace(oldValue, newValue))
						print("replaced" + oldValue +" with " + newValue)
			wf_tree.write(open(wfDirPath + '\\' + wf_file, 'wb'), encoding='UTF-8', xml_declaration=True, default_namespace=None, method="xml")	
						
	def updateSiDic(des_root):
		for si in des_root.findall("./Resources/ScreenDefinition/FusionScreenDefinition"):
			desSiDic[si.get('Name')] = si.get('myId')
		return des_root
			
	def mergePortalSI():
		des_tree = ET.parse(mergedProj + '\\' + des_portal_file)
		des_root = des_tree.getroot()
		desScreenDef = des_root.find("./Resources/ScreenDefinition")	
		des_root = updateSiDic(des_root)
		
		if desScreenDef is not None:
			for src_Si in src_root.iter('FusionScreenDefinition'):
				if src_Si.get('myId') == desSiDic.get(src_Si.get('Name')):
					oldSrcNameId = src_Si.get('myId')
					newSrcNameId = src_Si.get('myId') + "_src"
					src_Si.set('myId', newSrcNameId)
					src_Si.set('Name', newSrcNameId)
					print("renamed source Screen   :" +  src_Si.get("myId"))
					desScreenDef.append(src_Si)
					print('screen ' + newSrcNameId + 'is added')
					
					srcXmiId = src_Si.get('{http://www.omg.org/XMI}id')
					replaceScreenID_screen(oldSrcNameId, newSrcNameId, 'ScreenID' , srcXmiId, 'Screen')
					des_root = updateSiDic(des_root)
					#replace all src_Si.get('myId') and src_Si.get('Name')
					#which are contains src_Si.get('xmi:id') in  task screen
				else:
					desScreenDef.append(src_Si)
					print('screen ' + src_Si.get('Name') + 'is added')
				
				srcXmiId = src_Si.get('{http://www.omg.org/XMI}id')
				newDesScreenId = '../'+ des_portal_file + "#" + srcXmiId
				oldDesScreenId = '../'+ src_portal_file + "#" + srcXmiId				
				replaceScreenID_screen(oldDesScreenId, newDesScreenId, 'Screen' , srcXmiId, 'Screen')
				des_root = updateSiDic(des_root)
				#replace Screen portal name src_Si.get('xmi:id') in  task screen
			des_tree.write(open(mergedProj + '\\' + des_portal_file, 'wb'), encoding='UTF-8', xml_declaration=True, default_namespace=None, method="xml")		
		
	def updateWinDictionary(des_root):	
		#merge WindowsApplications	
		desWinAppDic.clear()
		for desWinApps in des_root.iter('WindowsApplications'):
			desWinAppDic[desWinApps.get('Name')] = {}
			for desElm in desWinApps.iter('elements'):
				desWinAppDic[desWinApps.get('Name')][desElm.get('Name')] = desElm.get("elementHandles")
		return des_root
		
	def mergePortalWindowApplicationElm():
		des_tree = ET.parse(mergedProj + '\\' + des_portal_file)
		des_root = des_tree.getroot()
		updateWinDictionary(des_root)

		#get allWindows and elements of win application
		for srcWinApps in src_root.iter('WindowsApplications'):	
			for srcElm in srcWinApps.iter('elements'):	
				if desWinAppDic.get(srcWinApps.get('Name')) is not None:
					if desWinAppDic.get(srcWinApps.get('Name')).get(srcElm.get('Name')) == srcElm.get("elementHandles"):	
						continue;
					else:
						#Replace xmi:id  of WindowsApplications in workflows of source	
						desWinApp = des_root.find(".//*[@Name='"+ srcWinApps.get('Name') +"']")
						replaceAppIdInWfs(srcWinApps.get('{http://www.omg.org/XMI}id'), desWinApp.get('{http://www.omg.org/XMI}id'), mergedProj + "\\workflows")
						
						allScreen = des_root.find(".//*[@Name='"+ srcWinApps.get('Name') +"']/allScreen")
						allScreen.append(srcElm)
						des_root = updateWinDictionary(des_root)
						print("added element : " + srcElm.get("elementHandles"))
				else:
					print("added application : " + srcWinApps.get('Name'))
					for apps in des_root.iter('Applications'):
						applications = apps
						break
					applications.append(srcWinApps)
					des_root = updateWinDictionary(des_root)
		des_tree.write(open(mergedProj + '\\' + des_portal_file, 'wb'), encoding='UTF-8', xml_declaration=True, default_namespace=None, method="xml")				

	def updateWebDictionary(des_root):
		#update dictionary WebApplications		
		for desWebApps in des_root.iter('WebApplications'):
			desWinAppDic[desWebApps.get('URL')] = {'flag' : 'exist'}
			for desPage in desWebApps.iter('pages'):
				desWinAppDic[desWebApps.get('URL')][desPage.get('fullUrl')] = {'flag' : 'exist'}
				for pageElm in desPage.iter('elements'):
					desWinAppDic[desWebApps.get('URL')][desPage.get('fullUrl')][pageElm.get('Name')] = pageElm.get("elementHandles")
		return des_root
		
	def mergePortalWebApplicationElm():
		des_tree = ET.parse(mergedProj + '\\' + des_portal_file)
		des_root = des_tree.getroot()
		updateWebDictionary(des_root)

		#get allPages and elements of page of application
		for srcWebApps in src_root.iter('WebApplications'):
			#check Applications
			if desWinAppDic.get(srcWebApps.get('URL')) is not None and desWinAppDic.get(srcWebApps.get('URL')).get('flag') == 'exist':
				for srcPage in srcWebApps.iter('pages'):
					#check pages
					if desWinAppDic.get(srcWebApps.get('URL')).get(srcPage.get('fullUrl')) is not None and desWinAppDic.get(srcWebApps.get('URL')).get(srcPage.get('fullUrl')).get('flag') == 'exist':
						#check elements
						for srcElm in srcPage.iter('elements'):	
							if desWinAppDic.get(srcWebApps.get('URL')).get(srcPage.get('fullUrl')).get(srcElm.get('Name')) == srcElm.get('elementHandles'):
								continue;
							else:
								for des_app in des_root.findall("./Resources/Applications/WebApplications"):
									if des_app.get('URL') == srcWebApps.get('URL'):
										for des_page in des_app.findall('./pages'):
											if srcPage.get('fullUrl') == des_page.get('fullUrl') and desWinAppDic.get(srcWebApps.get('URL')).get(srcPage.get('fullUrl')).get('flag') == 'exist':
												des_page.append(srcElm)
												des_root = updateWebDictionary(des_root) 
												print("added element : " + srcElm.get("elementHandles")	+ ' to page :'+ des_page.get('fullUrl'))
												desPageId = des_page.get('myId')
												srcPageId = srcPage.get('myId')
												if srcPageId != desPageId:
													replaceTaskPageId(srcPageId, desPageId, mergedProj + "\\workflows")
												break			
																	
					else:
						for app in des_root.findall("./Resources/Applications/WebApplications"):
							if app.get('URL') == srcWebApps.get('URL'):
								app.append(srcPage)
								des_root = updateWebDictionary(des_root)
								break
						print("added page : " + srcPage.get('fullUrl'))
			else:
				for src_application in des_root.iter('Applications'):
					applications = src_application
					break
				applications.append(srcWebApps)
				print("added application : " + srcWebApps.get('URL'))
				des_root = updateWebDictionary(des_root)
				
				#get des win App to update xmiId in workflows
				for desWebApp in des_root.findall("./Resources/Applications/WebApplications"):
					if desWebApp.get('URL') == srcWebApps.get('URL'):
						break
				replaceAppIdInWfs(srcWebApps.get('{http://www.omg.org/XMI}id'), desWebApp.get('{http://www.omg.org/XMI}id'), mergedProj + "\\workflows")
				print("add application : " + srcWebApps.get('Name'))
		des_tree.write(open(mergedProj + '\\' + des_portal_file, 'wb'), encoding='UTF-8', xml_declaration=True, default_namespace=None, method="xml")				

	def registerWfNameSpace():
		ET.register_namespace('bpmn2',"http://www.omg.org/spec/BPMN/20100524/MODEL") #some name
		ET.register_namespace('xs', "http://www.w3.org/2001/XMLSchema")
		ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")
		ET.register_namespace('bpmndi', "http://www.omg.org/spec/BPMN/20100524/DI")
		ET.register_namespace('dc', "http://www.omg.org/spec/DD/20100524/DC")
		ET.register_namespace('di', "http://www.omg.org/spec/DD/20100524/DI")

		
	def replaceAppIdInWfs(appId, newAppId, wfDirPath):
		registerWfNameSpace()
		for wf_file in os.listdir(wfDirPath):
			if wf_file.endswith(".fusionworkflow"):
				wf_tree = ET.parse(wfDirPath+"\\" + wf_file)			
				for elem in wf_tree.getiterator():
					currAppId = elem.get('ApplicationId')
					if currAppId is not None:
						if appId in currAppId:		
							elem.set('ApplicationId', elem.get('ApplicationId').replace(currAppId, '../'+ des_portal_file + "#" + newAppId))
							print("new applicationId for " + currAppId +" with " + '../'+ des_portal_file + "#" + newAppId)
			wf_tree.write(open(wfDirPath + '\\' + wf_file, 'wb'), encoding='UTF-8', xml_declaration=True, default_namespace=None, method="xml")				
			
	def replaceTaskPageId(pageId, newPageId, wfDirPath):
		registerWfNameSpace()
		for wf_file in os.listdir(wfDirPath):
			if wf_file.endswith(".fusionworkflow"):
				wf_tree = ET.parse(wfDirPath+"\\" + wf_file)			
				for elem in wf_tree.getiterator():
					currPageId = elem.get('pageId')
					if currPageId is not None:
						if pageId in currPageId:		
							elem.set('pageId', elem.get('pageId').replace(pageId, newPageId))
							print("new pageId for " + currPageId +" with " + pageId)
			wf_tree.write(open(wfDirPath + '\\' + wf_file, 'wb'), encoding='UTF-8', xml_declaration=True, default_namespace=None, method="xml")	
			
	def CopyDir(d_path, merProj):
		des = os.listdir(d_path)
		for name in des:
			full_name = os.path.join(d_path, name)
			if (os.path.isfile(full_name)):
				shutil.copy(full_name, merProj)
			else:
				try:
					os.mkdir(merProj + "\\"+ name)
					CopyDir(d_path +'\\'+ name, merProj + "\\"+ name)
				except:
					print("")
	try:
		shutil.rmtree('./mergedProj')	
	except Exception as e:	
		print('merProj dir cant be deleted exists')
	os.mkdir('mergedProj')	
	CopyDir(des_path, mergedProj)
	CopyDir(src_path + "\\workflows", mergedProj + "\\workflows")
	CopyDir(src_path + "\\resources", mergedProj + "\\resources")
	mergePortalWorkflowsElm()
	mergePortalSI()
	mergePortalSubflowsElm()
	mergePortalWindowApplicationElm()
	mergePortalWebApplicationElm()
	
master = Tk(className="Merge") 	
srcFile = ""
desFile = ""

def browseSrc():
	filename = askopenfilename(title = "Select source portal file",filetypes= (("fusion file","*.fusion_portal"),("all files","*.*")))
	global srcFile
	srcFile = filename
	T.config(state=NORMAL)
	T.delete('1.0', END)
	T.insert(INSERT, srcFile)
	T.config(state=DISABLED)
	print(srcFile)
	
def browseDes():
	filename = askopenfilename(title = "Select destination portal file",filetypes= (("fusion file","*.fusion_portal"),("all files","*.*")))
	global desFile
	desFile = filename
	T.config(state=NORMAL)
	T.delete('1.0', END)
	T.insert(INSERT, desFile)
	T.config(state=DISABLED)
	print(desFile)

def merge():
	print(srcFile)
	print(desFile)
	if srcFile!="" and desFile!="":
		main(srcFile, desFile)
		T.config(state=NORMAL)
		T.delete('1.0', END)
		T.insert(INSERT, os.getcwd() + '\\mergedProj')
		T.config(state=DISABLED)
	else:
		tkMessageBox.showerror("Error","Enter Source and Destination Path")

T = Text(master, height=3, width=25, bd=5, bg='#fdbf00')
T.pack()
Button(master, text="Source Portal", bg='#6bb6e6', width=30 , command=browseSrc).pack()
Button(master, text="Destination Portal",bg='#c7ffff', width=30 , command=browseDes).pack()
Button(master, text='Merge', bg="#07c", width=30,state='normal', command=merge).pack()
mainloop()