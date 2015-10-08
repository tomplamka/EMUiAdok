# -*- coding: utf-8 -*-
"""
/***************************************************************************
 EMUiAdok
                                 A QGIS plugin
 EMUiAdok
                              -------------------
        begin                : 2015-10-07
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Tomasz Hak
        email                : tomplamka@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from datetime import *
import getpass
import psycopg2
import sys
import os
import pdb
from PyQt4.QtXml import QDomDocument
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from EMUiAdok_dialog import EMUiAdokDialog
import os.path


class EMUiAdok:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'EMUiAdok_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = EMUiAdokDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&EMUiAdok')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'EMUiAdok')
        self.toolbar.setObjectName(u'EMUiAdok')
        
        #self.dlg.wybierzDokumentComboBox.addItem(u'Zaświadczenie')
        #self.dlg.wybierzDokumentComboBox.addItem(u'Zawiadomienie o ustaleniu nr')
        #self.dlg.wybierzDokumentComboBox.addItem(u'Zawiadomienie o zmianie nr')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('EMUiAdok', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/EMUiAdok/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'EMUiAdok'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&EMUiAdok'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
        
    def szukaj(self):
        # selekcja atrybutów na podstawie zaznaczonych wartości
        #self.iface.mapCanvas().setSelectionColor( QColor("yellow") )
        
        #wartości z coboBoxów do zmiennej
        varObreb = unicode(self.dlg.obrebComboBox.currentText())
        varNumer = unicode(self.dlg.dzialkaLineEdit.text())
        varArkusz = unicode(self.dlg.arkuszLineEdit.text())
        
        con = None

        try:
             
            con = psycopg2.connect(database='netgis_knurow', user='netgis_knurow', password='n4feqeTR', host='178.216.202.213')
            cur = con.cursor()
            
            data = (varObreb, varNumer, varArkusz)
            
            #nazwa ulicy
            query = "select nazwaglown from punkty_adresowe where obreb = %s AND numer = %s AND arkusz= %s;"
            cur.execute(query, data)
            con.commit()
            ulicaPA = cur.fetchone()[0]
            print ulicaPA

            #nazwa ulicy
            dataUpdate = (ulicaPA, varObreb, varNumer, varArkusz)
            query = "update emuia set nazwaglown = %s where rejon = %s AND numdzialki = %s AND arkusz= %s;"
            cur.execute(query, dataUpdate)
            con.commit()

            #TERYT ulicy
            query = "select ulica_ad_n from punkty_adresowe where obreb = %s AND numer = %s AND arkusz= %s;"
            cur.execute(query, data)
            con.commit()
            ulicaPAteryt = cur.fetchone()[0]
            ulicaPAteryt = str(ulicaPAteryt)

            #idTERYT ulicy
            dataUpdate = (ulicaPAteryt, varObreb, varNumer, varArkusz)
            query = "update emuia set ulica_ad_n = %s where rejon = %s AND numdzialki = %s AND arkusz= %s;"
            cur.execute(query, dataUpdate)
            con.commit()

            #numer porządkowy budynku
            query = "select numerporza from punkty_adresowe where obreb = %s AND numer = %s AND arkusz= %s;"
            cur.execute(query, data)
            con.commit()
            nrPorza = cur.fetchone()[0]

            #numer porządkowy budynku
            dataUpdate = (nrPorza, varObreb, varNumer, varArkusz)
            query = "update emuia set numerporza = %s where rejon = %s AND numdzialki = %s AND arkusz= %s;"
            cur.execute(query, dataUpdate)
            con.commit()

            #kod pocztowy
            query = "select kodpocztow from punkty_adresowe where obreb = %s AND numer = %s AND arkusz= %s;"
            cur.execute(query, data)
            con.commit()
            kodPoczt = cur.fetchone()[0]
            print kodPoczt

            #update pustych atrybutów dla wybranych wierszy
            #kod pocztowy
            dataUpdate = (kodPoczt, varObreb, varNumer, varArkusz)
            query = "update emuia set kodpocztow = %s where rejon = %s AND numdzialki = %s AND arkusz= %s;"
            cur.execute(query, dataUpdate)
            con.commit()
            
            


        except psycopg2.DatabaseError, e:
            if con:
                con.rollback()

            iface.messageBar().pushMessage(u'Błąd', u'Problem z połączeniem do bazy', level=QgsMessageBar.CRITICAL, duration=5)
            sys.exit(1)
            
            
        finally:
            
            if con:
                con.close()
                
            else:
                iface.messageBar().pushMessage(u'Błąd', u'Dane nie zostały zapisane', level=QgsMessageBar.CRITICAL, duration=5)
        
        
        warstwa = self.iface.mapCanvas().currentLayer()
        

        
        #request = QgsFeatureRequest().setFilterExpression( "\"OBREB\"='" + varObreb + "' OR \"NUMER\"='"+ varNumer + "'  OR \"ARKUSZ\"='"+ varArkusz + "'" )
        expr = QgsExpression( "\"rejon\"='" + varObreb + "' AND \"numdzialki\"='"+ varNumer + "'  AND \"arkusz\"='"+ varArkusz + "'" )
        it = warstwa.getFeatures( QgsFeatureRequest( expr ) )
        ids = [i.id() for i in it]
        warstwa.setSelectedFeatures( ids )
        self.idAtlas = int(ids[0])
        
        
        #zoom do wybranej działki
        #box = warstwa.boundingBoxOfSelected()
        #self.iface.mapCanvas().setExtent(box)
        #self.iface.mapCanvas().refresh()
        
    def printZaswiadczenie(self):
        alayer = self.iface.activeLayer()
        
        varObreb = unicode(self.dlg.obrebComboBox.currentText())
        varNumer = unicode(self.dlg.dzialkaLineEdit.text())
        varArkusz = unicode(self.dlg.arkuszLineEdit.text())
        
        expr = QgsExpression( "\"rejon\"='" + varObreb + "' AND \"numdzialki\"='"+ varNumer + "'  AND \"arkusz\"='"+ varArkusz + "'" )
        it = alayer.getFeatures( QgsFeatureRequest( expr ) )
        ids = [i.id() for i in it]
        alayer.setSelectedFeatures( ids )
        self.idAtlas = int(ids[0])
        # Dodaje wszystkie warstwy do widoku mapy
        myMapRenderer = self.iface.mapCanvas().mapRenderer()

        # ładuje szablon druku
        myComposition = QgsComposition(myMapRenderer)
        username = getpass.getuser()
        username = str(username)
        templateDir = r'C:\Users'
        endDir = '\Desktop\KnurowEMUiA\pliki\szablony druku'
        template = '\zaswiadczenie.qpt'
        #templateSuffix = '.qpt'
        
        myFile = os.path.join(templateDir, username + endDir + template)

        #myFile = r'C:\Users\haku\Desktop\Opole\Knurow\druk\zaswiadczenie.qpt'
        myTemplateFile = file(myFile, 'rt')
        myTemplateContent = myTemplateFile.read()
        myTemplateFile.close()


        myDocument = QDomDocument()
        myDocument.setContent(myTemplateContent)
        myComposition.loadFromTemplate(myDocument)

        # pobierz kompozycję mapy i zdefinuj skalę
        myAtlasMap = myComposition.getComposerMapById(0)
        
        # Konfiguracja Atlas
        myAtlas = myComposition.atlasComposition()#ustawia warstwę w atlasie
        
        myAtlas.setEnabled(True)
        myAtlas.setCoverageLayer(alayer)
        myAtlas.setHideCoverage(False)
        myAtlas.setSingleFile(True)
        myAtlas.setHideCoverage(False)
        
        myAtlasMap.setAtlasDriven(True)#mapa kontrolowana przez atlas
        myAtlasMap.setAtlasScalingMode(QgsComposerMap.Auto)# jaka skala kontrolowana przez atlas (margin)
        myComposition.setAtlasMode(QgsComposition.ExportAtlas)#Ustawia Atlas na Eksport do PDF

        myComposition.refreshItems()   
            # generuj atlas
        myAtlas.beginRender()
        
        myAtlas.prepareForFeature(self.idAtlas)
        saveDirEnd = '\Desktop\KnurowEMUiA\wydruki\zaswiadczenie'
        outputDir = os.path.join(templateDir, username + saveDirEnd)
        output_pdf = outputDir + "zaswiadczenie_nr_" + str(self.idAtlas)+ ".pdf"
        try:
            myComposition.exportAsPDF(output_pdf)
            myAtlas.endRender()
            self.iface.messageBar().pushMessage('Sukces', u'Zaświadczenie zostało wygenerowane pomyślnie', level=QgsMessageBar.SUCCESS, duration=5)
        except:
            self.iface.messageBar().pushMessage(u'Błąd', u'Generowanie Zaświadczenia nie powiodło sie', level=QgsMessageBar.CRITICAL, duration=5)
            
    def printZawiadomienieUstal(self):
        alayer = self.iface.activeLayer()
        
        varObreb = unicode(self.dlg.obrebComboBox.currentText())
        varNumer = unicode(self.dlg.dzialkaLineEdit.text())
        varArkusz = unicode(self.dlg.arkuszLineEdit.text())
        
        expr = QgsExpression( "\"rejon\"='" + varObreb + "' AND \"numdzialki\"='"+ varNumer + "'  AND \"arkusz\"='"+ varArkusz + "'" )
        it = alayer.getFeatures( QgsFeatureRequest( expr ) )
        ids = [i.id() for i in it]
        alayer.setSelectedFeatures( ids )
        self.idAtlas = int(ids[0])
        
        # Dodaje wszystkie warstwy do widoku mapy
        myMapRenderer = self.iface.mapCanvas().mapRenderer()

        # ładuje szablon druku
        myComposition = QgsComposition(myMapRenderer)
        username = getpass.getuser()
        username = str(username)
        templateDir = r'C:\Users'
        endDir = '\Desktop\KnurowEMUiA\pliki\szablony druku'
        template = '\zawiadomienie_o_ust.qpt'
        #templateSuffix = '.qpt'
        
        myFile = os.path.join(templateDir, username + endDir + template)

        #myFile = r'C:\Users\haku\Desktop\Opole\Knurow\druk\zaswiadczenie.qpt'
        myTemplateFile = file(myFile, 'rt')
        myTemplateContent = myTemplateFile.read()
        myTemplateFile.close()


        myDocument = QDomDocument()
        myDocument.setContent(myTemplateContent)
        myComposition.loadFromTemplate(myDocument)

        # pobierz kompozycję mapy i zdefinuj skalę
        myAtlasMap = myComposition.getComposerMapById(0)
        
        # Konfiguracja Atlas
        myAtlas = myComposition.atlasComposition()#ustawia warstwę w atlasie
        
        myAtlas.setEnabled(True)
        myAtlas.setCoverageLayer(alayer)
        myAtlas.setHideCoverage(False)
        myAtlas.setSingleFile(True)
        myAtlas.setHideCoverage(False)
        
        myAtlasMap.setAtlasDriven(True)#mapa kontrolowana przez atlas
        myAtlasMap.setAtlasScalingMode(QgsComposerMap.Auto)# jaka skala kontrolowana przez atlas (margin)
        myComposition.setAtlasMode(QgsComposition.ExportAtlas)#Ustawia Atlas na Eksport do PDF

        myComposition.refreshItems()   
            # generuj atlas
        myAtlas.beginRender()
        
        myAtlas.prepareForFeature(self.idAtlas)
        saveDirEnd = '\Desktop\KnurowEMUiA\wydruki\zawiadomienie_o_ustaleniu_nr'
        outputDir = os.path.join(templateDir, username + saveDirEnd)
        output_pdf = outputDir + "zaswiadczenie_nr_" + str(self.idAtlas)+ ".pdf"
        try:
            myComposition.exportAsPDF(output_pdf)
            myAtlas.endRender()
            self.iface.messageBar().pushMessage('Sukces', u'Zaświadczenie zostało wygenerowane pomyślnie', level=QgsMessageBar.SUCCESS, duration=5)
        except:
            self.iface.messageBar().pushMessage(u'Błąd', u'Generowanie Zaświadczenia nie powiodło sie', level=QgsMessageBar.CRITICAL, duration=5)
            
    def printZawiadomienieZmiana(self):
        alayer = self.iface.activeLayer()
        
        varObreb = unicode(self.dlg.obrebComboBox.currentText())
        varNumer = unicode(self.dlg.dzialkaLineEdit.text())
        varArkusz = unicode(self.dlg.arkuszLineEdit.text())
        
        expr = QgsExpression( "\"rejon\"='" + varObreb + "' AND \"numdzialki\"='"+ varNumer + "'  AND \"arkusz\"='"+ varArkusz + "'" )
        it = alayer.getFeatures( QgsFeatureRequest( expr ) )
        ids = [i.id() for i in it]
        alayer.setSelectedFeatures( ids )
        self.idAtlas = int(ids[0])
        
        # Dodaje wszystkie warstwy do widoku mapy
        myMapRenderer = self.iface.mapCanvas().mapRenderer()

        # ładuje szablon druku
        myComposition = QgsComposition(myMapRenderer)
        username = getpass.getuser()
        username = str(username)
        templateDir = r'C:\Users'
        endDir = '\Desktop\KnurowEMUiA\pliki\szablony druku'
        template = '\zawiadomienie_o_zm_nr.qpt'
        #templateSuffix = '.qpt'
        
        myFile = os.path.join(templateDir, username + endDir + template)

        #myFile = r'C:\Users\haku\Desktop\Opole\Knurow\druk\zaswiadczenie.qpt'
        myTemplateFile = file(myFile, 'rt')
        myTemplateContent = myTemplateFile.read()
        myTemplateFile.close()


        myDocument = QDomDocument()
        myDocument.setContent(myTemplateContent)
        myComposition.loadFromTemplate(myDocument)

        # pobierz kompozycję mapy i zdefinuj skalę
        myAtlasMap = myComposition.getComposerMapById(0)
        
        # Konfiguracja Atlas
        myAtlas = myComposition.atlasComposition()#ustawia warstwę w atlasie
        
        myAtlas.setEnabled(True)
        myAtlas.setCoverageLayer(alayer)
        myAtlas.setHideCoverage(False)
        myAtlas.setSingleFile(True)
        myAtlas.setHideCoverage(False)
        
        myAtlasMap.setAtlasDriven(True)#mapa kontrolowana przez atlas
        myAtlasMap.setAtlasScalingMode(QgsComposerMap.Auto)# jaka skala kontrolowana przez atlas (margin)
        myComposition.setAtlasMode(QgsComposition.ExportAtlas)#Ustawia Atlas na Eksport do PDF

        myComposition.refreshItems()   
            # generuj atlas
        myAtlas.beginRender()
        
        myAtlas.prepareForFeature(self.idAtlas)
        saveDirEnd = '\Desktop\KnurowEMUiA\wydruki\zawiadomienie_o_zmianie_nr'
        outputDir = os.path.join(templateDir, username + saveDirEnd)
        output_pdf = outputDir + "zaswiadczenie_nr_" + str(self.idAtlas)+ ".pdf"
        try:
            myComposition.exportAsPDF(output_pdf)
            myAtlas.endRender()
            self.iface.messageBar().pushMessage('Sukces', u'Zaświadczenie zostało wygenerowane pomyślnie', level=QgsMessageBar.SUCCESS, duration=5)
        except:
            self.iface.messageBar().pushMessage(u'Błąd', u'Generowanie Zaświadczenia nie powiodło sie', level=QgsMessageBar.CRITICAL, duration=5)


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        
        activeLyr=None
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            if lyr.name() == "emuia":
                activeLyr = lyr
                self.iface.setActiveLayer(activeLyr)
                
        self.dlg.btnZaswiadczenie.clicked.connect(self.printZaswiadczenie)
        self.dlg.btnZawiadomienieUstal.clicked.connect(self.printZawiadomienieUstal)
        self.dlg.btnZawiadomienieZmiana.clicked.connect(self.printZawiadomienieZmiana)
        self.dlg.btnSzukaj.clicked.connect(self.szukaj)
                
        self.dlg.obrebComboBox.clear()
        self.dlg.dzialkaLineEdit.clear()
        self.dlg.arkuszLineEdit.clear()
        
        warstwa = self.iface.activeLayer()
        
        #filtr Obręby
        obreb = warstwa.dataProvider().fieldNameIndex( 'rejon' ) 
        atrObreb = warstwa.dataProvider().uniqueValues( obreb )
        cbObreb = self.dlg.obrebComboBox.addItems( atrObreb )
        
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
