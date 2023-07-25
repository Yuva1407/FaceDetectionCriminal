#!/usr/bin/env python3
import sys
import sqlite3
import os
import face_recognition
import subprocess as sp

from database import Databases

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit, QMessageBox, QPushButton, QLabel, QGridLayout, \
    QWidget, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QIntValidator, QFont


class CriminalDatabaseManagementSystem(QMainWindow):
    def __init__(self):
        super(CriminalDatabaseManagementSystem, self).__init__()

        # DB Init
        if not os.path.exists(".database/PoliceDB.db"):
            db = Databases()
            db.PoliceDB()
        if not os.path.exists(".database/CriminalDB.db"):
            db = Databases()
            db.CriminalDB()

        # DB Connect
        self.conPD = sqlite3.connect(".database/PoliceDB.db")
        self.curPD = self.conPD.cursor()
        self.conCD = sqlite3.connect(".database/CriminalDB.db")
        self.curCD = self.conCD.cursor()

        # Globals
        self.Names = []
        self.Ids = []
        self.PhNos = []

        # Locals
        self.userId = None
        self.userPass = None
        self.userGen = "Male"
        self.msg = None

        # UI Init
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.showMaximized()
        self.loginWindow()

    # Login Window
    def loginWindow(self):
        loadUi(".layouts/loginWindow.ui", self)
        self.loginBtn.clicked.connect(self.loginFunction)
        self.newAccBtn.clicked.connect(self.regWindow)
        self.eyeBtn.clicked.connect(self.showPass)
        self.eyeBtn.setIcon(QIcon(".resource/eyeOpen.svg"))

    def loginFunction(self):
        self.userId = self.id.text()
        self.userPass = self.password.text()
        if self.checkIdAndPass(self.userId, self.userPass):
            self.msgBox(True, "Success", "Login Success", self.searchWindow)

    def checkIdAndPass(self, Id, Password):
        self.Ids = []
        self.conPD = sqlite3.connect(".database/PoliceDB.db")
        idCur = self.conPD.cursor()
        passCur = self.conPD.cursor()
        idCur.execute("Select Police_ID from Police_Login")
        ids = idCur.fetchall()
        for i in ids:
            self.Ids.append(i[0])
        if Id in self.Ids:
            passCur.execute("SELECT Password FROM Police_Login WHERE Police_ID = " + "'" + Id + "'")
            ps = passCur.fetchall()
            Pass = ps[0][0]
            if Password == Pass:
                return True
            else:
                self.msgBox(False, "Error", "Wrong Password!", None)
                return False
        else:
            self.msgBox(False, "Error", "Invalid Login Id!", None)

    # Register Window
    def regWindow(self):
        loadUi(".layouts/regWindow.ui", self)
        self.maleBtn.setChecked(True)
        self.eyeBtn.setIcon(QIcon(".resource/eyeOpen.svg"))
        self.maleBtn.stateChanged.connect(self.genderCheckM)
        self.femaleBtn.stateChanged.connect(self.genderCheckF)
        self.regBtn.clicked.connect(self.registerFunction)
        self.backBtn.clicked.connect(self.loginWindow)
        self.eyeBtn.clicked.connect(self.showPass)

    def genderCheckM(self):
        if self.maleBtn.isChecked():
            self.femaleBtn.setChecked(False)
            self.userGen = "Male"

    def genderCheckF(self):
        if self.femaleBtn.isChecked():
            self.maleBtn.setChecked(False)
            self.userGen = "Female"

    def registerFunction(self):
        userName = self.name.text()
        userRank = self.rank.text()
        userPoliceID = self.policeId.text()
        userDob = self.dob.text()
        userState = self.state.text()
        userDist = self.dist.text()
        userBranch = self.branch.text()
        userPass = self.password.text()
        userRePass = self.repassword.text()
        userPhNo = self.phNo.text()
        userEmail = self.emailId.text()
        if self.checkRegister(userName, userRank, userPoliceID, userDob, userState, userDist, userBranch, self.userGen,
                              userPass, userRePass, userPhNo, userEmail):
            self.msgBox(True, "Success", "Register Success", self.loginWindow)

    def checkRegister(self, name, rank, pid, dob, state, dist, branch, gen, passwd, re_passwd, ph, email):
        if not (
                name == "" or rank == "" or pid == "" or dob == "" or state == "" or dist == "" or branch == "" or gen == "" or passwd == "" or re_passwd == "" or ph == "" or email == ""):
            if passwd == re_passwd:
                self.curPD.execute(
                    "INSERT INTO Police_Details VALUES (" + "'" + name + "'," + "'" + rank + "'," + "'" + pid + "'," + "'" + dob + "'," + "'" + state + "'," + "'" + dist + "'," + "'" + branch + "'," + "'" + gen + "'," + "'" + ph + "'," + "'" + email + "'" + ")")
                self.curPD.execute(
                    "INSERT INTO Police_Login VALUES (" + "'" + pid + "'," + "'" + passwd + "'," + "'" + re_passwd + "'" + ")")
                self.conPD.commit()
                return True
            else:
                self.msgBox(False, "Error", "Password Doesn't Match!!!", None)
        else:
            self.msgBox(False, "Error", "Fill All Details!", None)
        return False

    # Search Window
    def searchWindow(self):
        loadUi(".layouts/searchWindow.ui", self)
        self.searchBtn.clicked.connect(self.search)
        self.cameraView.mousePressEvent = self.captureSearchImage
        self.imgSearchBtn.clicked.connect(self.imgSearch)
        self.newCaseFileBtn.clicked.connect(self.newCaseWindow)
        self.signOutBtn.clicked.connect(self.signOut)

    def search(self):
        self.curCD.execute("SELECT Name, ID, Phone_number FROM Criminal_Details")
        details = self.curCD.fetchall()
        for i in details:
            self.Names.append(i[0])
            self.Ids.append(i[1])
            self.PhNos.append(i[2])
        self.listViewWindow(self.searchLine.text())
        self.Names.clear()
        self.Ids.clear()
        self.PhNos.clear()

    def imgSearch(self):
        noFace = False
        res = []
        res_dict = {}
        myList = os.listdir(".images")
        for i in range(len(myList)):
            searchImg = face_recognition.load_image_file(".temp/temp.jpg")
            dbImg = face_recognition.load_image_file('.images/' + myList[i])
            try:
                encode_search_img = face_recognition.face_encodings(searchImg)[0]
                encode_db_img = face_recognition.face_encodings(dbImg)[0]
                results = face_recognition.compare_faces([encode_search_img], encode_db_img)
                faceDis = face_recognition.face_distance([encode_search_img], encode_db_img)
                if results[0]:
                    res.append(faceDis[0])
                    res_dict.update({faceDis[0]: myList[i]})
            except IndexError:
                noFace = True
        try:
            true = min(res)
            os.remove(".temp/temp.jpg")
            self.detailsView(res_dict[true].replace(".jpg", ""))
        except ValueError:
            if noFace:
                self.msgBox(False, "No Match", "Given Image Doesn't Have any Face", None)
            else:
                self.msgBox(False, "No Match", "Given Image Doesn't Match any Criminal in the DB", None)

    def detailsView(self, Id):
        self.curCD.execute(
            "SELECT Name, ID, Age, Gender, Phone_number, Address, No_of_cases, No_of_yrs_prisoned, Case_history FROM Criminal_Details WHERE ID = '" + Id + "'")
        details = self.curCD.fetchall()
        Name = details[0][0]
        ID = details[0][1]
        Age = details[0][2]
        Gender = details[0][3]
        PhNo = details[0][4]
        Address = details[0][5]
        NoOfCases = details[0][6]
        NoOfYrsPrisoned = details[0][7]
        CaseHistory = details[0][8]
        self.viewCriminalDetailsWindow(Name, ID, Age, Gender, PhNo, Address, NoOfCases, NoOfYrsPrisoned, CaseHistory)

    def captureSearchImage(self, event):
        sp.check_call("python3 capture.py", shell=True)
        pix = QPixmap(".temp/temp.jpg")
        self.cameraView.setPixmap(pix)

    def signOut(self):
        if os.path.exists(".temp/temp.jpg"):
            os.remove(".temp/temp.jpg")
        self.loginWindow()

    # List View Window
    def listViewWindow(self, Txt):
        loadUi(".layouts/listWindow.ui", self)
        self.cancelBtn.clicked.connect(self.searchWindow)
        for i in range(len(self.Names)):
            if Txt.lower() in self.Names[i].lower() or Txt.lower() in self.Ids[i] or Txt.lower() in self.PhNos[i]:
                self.cardWidget(self.Names[i], self.Ids[i], self.PhNos[i])

    # Card Widget
    def cardWidget(self, Name, Id, PhNo):
        Form = QWidget(self.scrollAreaWidgetContents)
        Form.setObjectName(u"Form")
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.resize(800, 200)
        Form.setMinimumSize(QSize(0, 200))
        Form.setMaximumSize(QSize(16777210, 200))
        Form.setStyleSheet("#Form{border: 2px solid #000; background-color: rgb(119, 118, 123);}")
        horizontalLayout = QHBoxLayout(Form)
        label = QLabel(Form)
        label.setMinimumSize(QSize(180, 180))
        label.setMaximumSize(QSize(180, 16777215))
        label.setStyleSheet(u"border: 2px solid #000;")
        label.setPixmap(QPixmap(".images/" + Id + ".jpg"))
        label.setScaledContents(True)
        horizontalLayout.addWidget(label)
        widget = QWidget(Form)
        gridLayout = QGridLayout(widget)
        idLabel = QLabel(widget)
        idLabel.setMinimumSize(QSize(0, 35))
        font = QFont()
        font.setPointSize(15)
        idLabel.setFont(font)
        idLabel.setText("ID")
        gridLayout.addWidget(idLabel, 1, 0, 1, 1)
        nameLabel = QLabel(widget)
        nameLabel.setMinimumSize(QSize(0, 35))
        nameLabel.setFont(font)
        nameLabel.setText("Name")
        gridLayout.addWidget(nameLabel, 0, 0, 1, 1)
        name = QLineEdit(widget)
        name.setMinimumSize(QSize(0, 35))
        name.setFont(font)
        name.setReadOnly(True)
        name.setText(Name)
        gridLayout.addWidget(name, 0, 1, 1, 1)
        phNoLabel = QLabel(widget)
        phNoLabel.setMinimumSize(QSize(0, 35))
        phNoLabel.setFont(font)
        phNoLabel.setText("Phone No")
        gridLayout.addWidget(phNoLabel, 2, 0, 1, 1)
        idEdit = QLineEdit(widget)
        idEdit.setMinimumSize(QSize(0, 35))
        idEdit.setFont(font)
        idEdit.setReadOnly(True)
        idEdit.setText(Id)
        gridLayout.addWidget(idEdit, 1, 1, 1, 1)
        phNo = QLineEdit(widget)
        phNo.setMinimumSize(QSize(0, 35))
        phNo.setFont(font)
        phNo.setReadOnly(True)
        phNo.setText(PhNo)
        gridLayout.addWidget(phNo, 2, 1, 1, 1)
        viewBtn = QPushButton(widget)
        viewBtn.setMinimumSize(QSize(100, 35))
        viewBtn.setMaximumSize(QSize(100, 16777215))
        viewBtn.setFont(font)
        viewBtn.setText("View")
        viewBtn.clicked.connect(lambda check, arg=Id: self.detailsView(arg))
        gridLayout.addWidget(viewBtn, 3, 1, 1, 1)
        horizontalLayout.addWidget(widget)
        self.layoutCard.setAlignment(Qt.AlignTop)
        self.layoutCard.addWidget(Form)

    # New Case Window
    def newCaseWindow(self):
        loadUi(".layouts/newCaseWindow.ui", self)
        self.maleBtn.setChecked(True)
        self.maleBtn.stateChanged.connect(self.genderCCheckM)
        self.femaleBtn.stateChanged.connect(self.genderCCheckF)
        self.othersBtn.stateChanged.connect(self.genderCCheckO)
        self.cPhNo.setValidator(QIntValidator())
        self.cPhNo.setMaxLength(10)
        self.cameraView.mousePressEvent = self.captureCriminalImage
        self.submitBtn.clicked.connect(lambda: self.submitFunction("submit"))
        self.cancelBtn.clicked.connect(self.searchWindow)

    def genderCCheckM(self):
        if self.maleBtn.isChecked():
            self.femaleBtn.setChecked(False)
            self.othersBtn.setChecked(False)
            self.userGen = "Male"

    def genderCCheckF(self):
        if self.femaleBtn.isChecked():
            self.maleBtn.setChecked(False)
            self.othersBtn.setChecked(False)
            self.userGen = "Female"

    def genderCCheckO(self):
        if self.othersBtn.isChecked():
            self.maleBtn.setChecked(False)
            self.femaleBtn.setChecked(False)
            self.userGen = "Others"

    def submitFunction(self, state):
        cName = self.cName.text()
        cId = self.cId.text()
        cAge = self.cAge.text()
        cPhNo = self.cPhNo.text()
        cAddress = self.cAddress.toPlainText()
        cNoOfCases = self.cNoOfCases.text()
        cNoOfYrsPrison = self.cNoOfYrsPrison.text()
        cCaseHistory = self.cCaseHistory.toPlainText()
        if self.checkSubmit(cName, cId, cAge, self.userGen, cPhNo, cAddress, cNoOfCases, cNoOfYrsPrison, cCaseHistory,
                            state):
            if state == "submit":
                self.msgBox(True, "Success", "New Case File Created Id:" + cId + " Name:" + cName, self.clear)
            elif state == "update":
                self.msgBox(True, "Success", "Id:" + cId + " Name:" + cName + " Case File Updated", self.clear)

    def checkSubmit(self, Name, Id, Age, Gen, PhNo, Address, Cases, YearsPrison, History, submitState):
        if not (
                Name == "" or Id == "" or Age == "" or Gen == "" or PhNo == "" or Address == "" or Cases == "" or YearsPrison == "" or History == ""):
            if os.path.exists(".images/" + Id + ".jpg"):
                if submitState == "submit":
                    self.curCD.execute(
                        "INSERT INTO Criminal_Details VALUES (" + "'" + Name + "'," + "'" + Id + "'," + "'" + Age + "'," + "'" + Gen + "'," + "'" + PhNo + "'," + "'" + Address + "'," + "'" + Cases + "'," + "'" + YearsPrison + "'," + "'" + History + "'" + ")")
                    self.conCD.commit()
                elif submitState == "update":
                    self.curCD.execute(
                        "UPDATE Criminal_Details SET Name=" + "'" + Name + "', ID=" + "'" + Id + "', Age=" + "'" + Age + "', Gender=" + "'" + Gen + "', Phone_number=" + "'" + PhNo + "', Address=" + "'" + Address + "', No_of_cases=" + "'" + Cases + "', No_of_yrs_prisoned=" + "'" + YearsPrison + "', Case_history=" + "'" + History + "' WHERE ID=" + "'" + Id + "'")
                    self.conCD.commit()
                return True
            else:
                self.msgBox(False, "Error", "Capture Criminal Image to Submit", None)
        else:
            self.msgBox(False, "Error", "Fill All Details", None)
        return False

    def captureCriminalImage(self, event):
        if not self.cId.text() == "":
            sp.check_call("python3 capture.py -d images -f" + self.cId.text(), shell=True)
            pix = QPixmap(".images/" + self.cId.text() + ".jpg")
            self.cameraView.setPixmap(pix)
        else:
            self.msgBox(False, "Error", "Enter Criminal Id to Capture Image", None)

    # Criminal Details View Window
    def viewCriminalDetailsWindow(self, Name, Id, Age, Gen, PhNo, Address, Cases, YearsPrison, History):
        loadUi(".layouts/newCaseWindow.ui", self)
        self.cName.setReadOnly(True)
        self.cId.setReadOnly(True)
        self.cAge.setReadOnly(True)
        if Gen == "Male":
            self.maleBtn.setChecked(True)
            self.femaleBtn.setCheckable(False)
            self.othersBtn.setCheckable(False)
        elif Gen == "Female":
            self.maleBtn.setCheckable(False)
            self.femaleBtn.setChecked(True)
            self.othersBtn.setCheckable(False)
        elif Gen == "Others":
            self.maleBtn.setCheckable(False)
            self.femaleBtn.setCheckable(False)
            self.othersBtn.setChecked(True)
        self.cPhNo.setReadOnly(True)
        self.cAddress.setReadOnly(True)
        self.cNoOfCases.setReadOnly(True)
        self.cNoOfYrsPrison.setReadOnly(True)
        self.cCaseHistory.setReadOnly(True)
        self.cameraView.mousePressEvent = None
        self.cancelBtn.clicked.connect(self.searchWindow)
        self.deleteBtn.setEnabled(True)
        self.deleteBtn.clicked.connect(lambda: self.deleteCriminalDetails(Id))
        self.submitBtn.setText("Edit")
        self.submitBtn.clicked.connect(self.editCriminalDetails)
        # Set Values
        self.cName.setText(Name)
        self.cId.setText(Id)
        self.cAge.setValue(int(Age))
        if Gen == "Male":
            self.maleBtn.setChecked(True)
        elif Gen == "Female":
            self.femaleBtn.setChecked(True)
        elif Gen == "Others":
            self.othersBtn.setChecked(True)
        self.cPhNo.setText(PhNo)
        self.cAddress.setText(Address)
        self.cNoOfCases.setValue(int(Cases))
        self.cNoOfYrsPrison.setValue(float(YearsPrison))
        self.cCaseHistory.setText(History)
        self.cameraView.setPixmap(QPixmap(".images/" + Id + ".jpg"))

    def editCriminalDetails(self):
        self.cName.setReadOnly(False)
        self.cId.setReadOnly(True)
        self.cAge.setReadOnly(False)
        self.maleBtn.setCheckable(True)
        self.femaleBtn.setCheckable(True)
        self.othersBtn.setCheckable(True)
        self.cPhNo.setReadOnly(False)
        self.cAddress.setReadOnly(False)
        self.cNoOfCases.setReadOnly(False)
        self.cNoOfYrsPrison.setReadOnly(False)
        self.cCaseHistory.setReadOnly(False)
        self.cameraView.mousePressEvent = self.captureCriminalImage
        self.cancelBtn.clicked.connect(self.searchWindow)
        self.deleteBtn.setEnabled(True)
        self.submitBtn.setText("Submit")
        self.submitBtn.clicked.connect(lambda: self.submitFunction("update"))

    def deleteCriminalDetails(self, Id):
        self.curCD.execute("DELETE FROM Criminal_Details WHERE ID=" + "'" + Id + "'")
        self.conCD.commit()
        if os.path.exists(".images/" + Id + ".jpg"):
            os.remove(".images/" + Id + ".jpg")
        self.searchWindow()

    # Functions
    def showPass(self):
        if self.password.text() != "" and self.password.echoMode() == QLineEdit.Password:
            self.password.setEchoMode(QLineEdit.Normal)
            self.eyeBtn.setIcon(QIcon(".resource/eyeClosed.svg"))
        else:
            self.password.setEchoMode(QLineEdit.Password)
            self.eyeBtn.setIcon(QIcon(".resource/eyeOpen.svg"))

    def clear(self):
        self.cName.clear()
        self.cId.clear()
        self.cAge.setValue(18)
        self.cPhNo.clear()
        self.cAddress.clear()
        self.cNoOfCases.setValue(1)
        self.cNoOfYrsPrison.setValue(0.0)
        self.cCaseHistory.clear()
        self.cameraView.setText(
            "Click Here to open Camera and Press Space Bar to Capture (or) Press 'C' to Close Camera")

    # Message Box
    def msgBox(self, msgType, msgTitle, message, ui):
        self.msg = QMessageBox()
        self.msg.setWindowFlag(Qt.WindowMinimizeButtonHint, False)
        self.msg.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.msg.setWindowTitle(msgTitle)
        self.msg.setText(message)
        if msgType:
            self.msg.setIcon(QMessageBox.Information)
            self.msg.setStandardButtons(QMessageBox.Ok)
            self.msg.buttonClicked.connect(ui)
        else:
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.setStandardButtons(QMessageBox.Ok)
        self.msg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = CriminalDatabaseManagementSystem()
    win.show()
    sys.exit(app.exec_())
