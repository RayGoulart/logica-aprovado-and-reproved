import sys
import queue
import time
from PySide6.QtNetwork import QLocalServer, QLocalSocket, QTcpServer, QHostAddress
import platform
from src.common.Enum.InspetionResult import InspectionResult
from src.view.second_screen.ui_second_screen import Ui_MainWindow
from src.common.Enum.InspetionResult import InspectionResult
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
                               QMainWindow, QPushButton, QSizePolicy, QWidget)
from PySide6.QtCore import Qt, QTimer


class SecondScreen(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(SecondScreen, self).__init__()
        self.setupUi(self)
        self.__configuranting_server()
        self.set_time_placards()
        self.confing_history()

    def __configuranting_server(self):
        system = sys.platform
        if system == "linux":
            self._server = QLocalServer(self)
            self._server.listen("/tmp/IHM")
        else:
            self._address = QHostAddress()
            self._address.setAddress("127.0.0.1")
            self._server = QTcpServer(self)
            self._server.listen(self._address, 1111)

        self._server.newConnection.connect(self.__on_new_connection)

    def __on_new_connection(self):
        self._client: QLocalSocket = self._server.nextPendingConnection()
        self._client and self._client.readyRead.connect(self.handle_request)
        self._client.disconnected.connect(self.__on_client_disconnected)

    def __on_client_disconnected(self):
        print("Client disconnected")
        self._client.deleteLater()
        self._client = None

    def handle_request(self):
        req = self._client.readAll()
        result = InspectionResult.convert_to_enum(req)
        self.enum_to_history(result)
        self.mostrar_aprovado_reprovado(result)
        #colocar os componentes que irão receber os enums

    def closeEvent(self, event):
        self._server.close()
        event.accept()

    def change_placard(self): #Fazer a parte do inspection com o Enum
        if self.show_placard:
            self.placard_team.setVisible(True)
            self.placard_jiga.setVisible(False)
        else:
            self.placard_team.setVisible(False)
            self.placard_jiga.setVisible(True)

        self.show_placard = not self.show_placard

    def set_name_switch(self, name_switch):
        self.switch_model.setText(f'{name_switch}')

    def set_time_placards(self):
        self.time = QTimer()
        self.time.timeout.connect(self.change_placard)
        self.time.start(3000)
        self.show_placard = True

    def enum_to_history(self, result):
        #criar a fila
        if result == InspectionResult.APROVADO:
            obj = self.queue_hisory.get()
            obj.setText(f'APROVADO')
            obj.setStyleSheet(u"background-color: #00A336; color: white;")
        

        elif result == InspectionResult.REPROVADO:
            obj = self.queue_hisory.get()
            obj.setText(f'REPROVADO')
            obj.setStyleSheet(u"background-color: #ff0000; color: white;")
        

        if self.queue_hisory.empty():
            self.label_product_one.setText("INSPECIONANDO...")
            self.label_product_one.setStyleSheet("background-color: yellow")

            self.label_product_two.setText("INSPECIONANDO...")
            self.label_product_two.setStyleSheet("background-color: yellow")

            self.label_product_three.setText("INSPECIONANDO...")
            self.label_product_three.setStyleSheet("background-color: yellow")
            self.confing_history()

    def confing_history(self):
            self.queue_hisory = queue.Queue()
            self.queue_hisory.put(self.label_product_one)
            self.queue_hisory.put(self.label_product_two)
            self.queue_hisory.put(self.label_product_three)

    def mostrar_aprovado_reprovado(self, resultado: InspectionResult):
        if resultado == InspectionResult.APROVADO:
            self.approved_product.setVisible(True)
            time.sleep(6)
            self.approved_product.setVisible(False)

        elif resultado == InspectionResult.REPROVADO:
            self.rejected_product.setVisible(True)
            time.sleep(6)
            self.rejected_product.setVisible(False)



    