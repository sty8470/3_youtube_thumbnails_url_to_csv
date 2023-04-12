import sys
import os
import threading
import re
  
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt

from crawl_youtube_thumbnails import YCrawler
from elapse_timer import TimeDisplayWorker

current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '../')))
sys.path.append(os.path.normpath(os.path.join(current_path, '../../')))

class YCrawlerUI(QDialog):
    def __init__(self):
        super().__init__()
        self.save_file_init_dir_path = current_path
        self.is_accepted = False
        self.yc = YCrawler(self)  
        self.crawler_thread = threading.Thread(target = self.yc.run)
        self.time_worker = TimeDisplayWorker(self)
        self.init_gui()

    def init_gui(self):
        self.setWindowIcon(QIcon(os.path.join(current_path, '../img/youtube.png')))
        self.setWindowTitle('유투브 썸네일 다운로드')
    
        self.main_v_layout = QVBoxLayout()

        # 검색어와 관련된 위젯 정렬
        self.search_h_layout = QHBoxLayout()
        self.search_label = QLabel("검색어: ")
        self.search_label.setFixedWidth(40)
        self.search_line_edit = QLineEdit("예: 손흥민 하이라이트")
        
        self.search_h_layout.addWidget(self.search_label)
        self.search_h_layout.addWidget(self.search_line_edit)
        self.search_h_layout.setAlignment(Qt.AlignLeft)
        
        # 최대 개수와 관련된 위젯 정렬
        self.max_num_h_layout = QHBoxLayout()
        self.max_num_label = QLabel("최대 썸네일 수: ")
        self.max_num_line_edit = QLineEdit("예: 100장")
        
        self.max_num_h_layout.addWidget(self.max_num_label)
        self.max_num_h_layout.addWidget(self.max_num_line_edit)
        self.max_num_h_layout.setAlignment(Qt.AlignLeft)
        
        # 저장 파일 경로와 관련된 위젯 정렬
        self.save_file_h_layout = QHBoxLayout()
        self.save_file_dir = QLabel("저장할 디렉토리: ")
        self.save_file_line_edit = QLineEdit()
        self.save_file_dir_button = QPushButton()
        self.save_file_dir_icon = self.style().standardIcon(getattr(QStyle, 'SP_DirIcon'))
        self.save_file_dir_button.setIcon(self.save_file_dir_icon)
        
        self.save_file_line_edit.setText(self.save_file_init_dir_path)
        self.save_file_dir_button.clicked.connect(self.find_safe_dir_to_save)

        self.save_file_h_layout.addWidget(self.save_file_dir)
        self.save_file_h_layout.addWidget(self.save_file_line_edit)
        self.save_file_h_layout.addWidget(self.save_file_dir_button)

        # 스탑워치 위젯 정렬
        self.stop_watch_h_layout = QHBoxLayout()
        self.stop_watch_label = QLabel("걸리는 시간: ")
        self.stop_watch_real_time_label = QLabel()

        self.stop_watch_h_layout.addWidget(self.stop_watch_label)
        self.stop_watch_h_layout.addWidget(self.stop_watch_real_time_label)
        
        self.submission_h_layout = QHBoxLayout()
        self.execute_button = QPushButton("실행")
        self.cancel_button = QPushButton("취소")
        
        self.execute_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.close)
        
        self.submission_h_layout.addWidget(self.execute_button)
        self.submission_h_layout.addWidget(self.cancel_button)
        
        self.main_v_layout.addLayout(self.search_h_layout)
        self.main_v_layout.addLayout(self.max_num_h_layout)
        self.main_v_layout.addLayout(self.save_file_h_layout)
        self.main_v_layout.addLayout(self.stop_watch_h_layout)
        self.main_v_layout.addLayout(self.submission_h_layout)
        
        self.main_v_layout.setContentsMargins(20, 10, 20, 10)
        self.setLayout(self.main_v_layout)
        self.setGeometry(300, 300, 400, 200)
        self.showDialog()
    
    def find_safe_dir_to_save(self):
        self.save_file_dir_path = QFileDialog.getExistingDirectory(QFileDialog(),
                                                              caption="저장할 올바른 디렉토리를 선택하세요",
                                                              directory=self.save_file_init_dir_path, 
                                                              options=QFileDialog.DontUseNativeDialog)

        if self.save_file_dir_path != '':
            self.save_file_line_edit.setText(self.save_file_dir_path)
        self.save_file_init_dir_path = self.save_file_line_edit.text()

    def accept(self):  
        if self.search_line_edit.text().strip() == '':
                QMessageBox.warning(self, "경고 메세지", "찾을 검색어를 입력해주세요!")
                return
        if self.max_num_line_edit.text().strip() == '':
            QMessageBox.warning(self, "경고 메세지", "다운로드 받을 썸네일 개수를 입력해주세요!")
            return
        if self.save_file_line_edit.text().strip() == '':
            QMessageBox.warning(self, "경고 메세지", "다운받을 디렉토리 경로를 설정해주세요!")
            return
        if re.findall(r'\d+', self.max_num_line_edit.text().strip()) == []:
            QMessageBox.warning(self, "경고 메세지", "다운받을 썸네일 개수에 정수값을 입력해주세요!")
            return  
        
        # 크롤러 셋팅
        self.yc = YCrawler(self)  
        self.crawler_thread = threading.Thread(target = self.yc.run)
        # 타이머 셋팅
        self.time_worker = TimeDisplayWorker(self)
        self.time_worker.time_signal.connect(self.func_time_emit)
        self.time_worker.job_finished_signal.connect(self.finish_crawling_job)
        self.time_worker.start()
        self.is_accepted = True
        # crawler_thread를 시작해준다.
        self.crawler_thread.start()

    def close(self):
        if self.time_worker.isRunning():
            self.time_worker.quit()
        if self.crawler_thread.is_alive():
            self.crawler_thread.quit()
        self.done(0)

    @QtCore.pyqtSlot(int)
    def func_time_emit(self, display_time):
        self.stop_watch_real_time_label.setText(str(display_time)+"초")
    
    @QtCore.pyqtSlot()
    def finish_crawling_job(self):
        if self.time_worker.job_finished_signal:
            QMessageBox.information(self, "Finished", "모든 크롤링이 정상적으로 종료되었습니다.")

    def showDialog(self):
        return super().exec_()

if __name__ == '__main__':
    app = QApplication([])
    win = YCrawlerUI()
    sys.exit(app.exec_())