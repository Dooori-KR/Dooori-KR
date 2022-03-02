import sys
import ccxt
import pandas as pd
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import time
import datetime
import requests

def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization":"Bearer "+token},
        data={"channel":channel,"text":text}
    )
    print(response)

myToken = "Your Token Name"

tickers=['BTC/USDT','ETH/USDT','XRP/USDT','SOL/USDT']
form_class=uic.loadUiType("bull.ui")[0]
binance=ccxt.binance()


class Worker(QThread):
    finished=pyqtSignal(dict)

    def run(self):
        turnimpulse=0
        gg2=0
        while True:
            data = {}
            now=datetime.datetime.now().time()
            now=str(now)[:8]

            for ticker in tickers:
                data[ticker]=self.get_market_infos(ticker,now)
                isimpulse=self.get_market_infos(ticker,now)[5]
                isstate=self.get_market_infos(ticker,now)[2]
                price=binance.fetch_ticker(ticker)['close']
                gg=self.get_market_infos(ticker,now)[6]
            if turnimpulse==0:
                post_message(myToken,'#stock',now+" 프로그램을 시작합니다")
            elif turnimpulse!=isimpulse:
                post_message(myToken,'#stock',"현재시간 : "+now+"\n비트코인 3시간 동향(1.5%등하락) : "+isimpulse+"\n비트코인 현재가 : "+str(price)+"\n비트코인 장세 : "+str(isstate))
            turnimpulse=isimpulse
            if gg2==0:
                pass
            if gg=="No Signal":
                pass
            elif gg2!=gg:
                if gg=="JUMP":
                    post_message(myToken,'#stock',"급등 신호 발생")
                if gg=="DROP":
                    post_message(myToken,'#stock',"급락 신호 발생")
            gg2=gg
            self.finished.emit(data)
            time.sleep(0.1)

    def get_market_infos(self,ticker,now):
        try:
            btc_ohlc=binance.fetch_ohlcv(ticker,'1m',limit=200)
            df=pd.DataFrame(btc_ohlc,columns=['datetime(UTC)','open','high','low','close','volume'])
            kst=[]
            for i in btc_ohlc:
                kst.append(i[0]+32400000)
            kst=pd.Series(kst)
            df['datetime(KST)']=kst
            df['datetime(UTC)']=pd.to_datetime(df['datetime(UTC)'],unit='ms')
            df['datetime(KST)']=pd.to_datetime(df['datetime(KST)'],unit='ms')
            df.set_index('datetime(KST)',inplace=True)
            
            ma5=df['close'].rolling(180).mean()
            last_ma5=round(ma5[-2],4)

            price=binance.fetch_ticker(ticker)['close']
            state=None
            impulse=None
            gdgr=None
            i=0
            last180=min(df['low'][-180:-1])*1.015 < max(df['high'][-180:-1])
            
            if df['close'][-2]*1.004 < price:
                gdgr="JUMP"
            elif df['close'][-2] > price*1.004:
                gdgr="DROP"
            else:
                gdgr="No Signal"

            if price > last_ma5:
                state = "Bullish"
            else:
                state = "Bearish"
            if last180:
                impulse = "Impulsive"
            else:
                impulse = "Not Impulsive"
            
            _min=min(df['low'][-180:-1])
            _max=max(df['high'][-180:-1])

            return str(price)+"$",str(last_ma5)+"$",state,str(_min)+"$",str(_max)+"$",impulse,gdgr
            
        except:
            return None, None, None, None, None, None, None


class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.tableWidget.setRowCount(len(tickers))
        self.worker=Worker()
        self.worker.finished.connect(self.update_table_widget)
        self.worker.start()
        self.timer=QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.inquiry)

    def inquiry(self):
        cur_time = QTime.currentTime()
        str_time = cur_time.toString("hh:mm:ss")
        self.statusBar().showMessage(str_time)

    @pyqtSlot(dict)
    def update_table_widget(self,data):
        try:
            for ticker, infos in data.items():
                index=tickers.index(ticker)

                self.tableWidget.setItem(index,0,QTableWidgetItem(ticker))
                self.tableWidget.setItem(index,1,QTableWidgetItem(str(infos[0])))
                self.tableWidget.setItem(index,2,QTableWidgetItem(str(infos[1])))
                self.tableWidget.setItem(index,3,QTableWidgetItem(str(infos[2])))
                self.tableWidget.setItem(index,4,QTableWidgetItem(str(infos[3])))                
                self.tableWidget.setItem(index,5,QTableWidgetItem(str(infos[4]))) 
                self.tableWidget.setItem(index,6,QTableWidgetItem(str(infos[5])))                 
                self.tableWidget.setItem(index,7,QTableWidgetItem(str(infos[6]))) 
        except:
            pass

app=QApplication(sys.argv)
mywindow=MyWindow()
mywindow.show()
app.exec_()
aa=datetime.datetime.now().time()
aa=str(aa)[:8]
post_message(myToken,'#stock',aa+" 프로그램을 종료합니다")
print(aa+" 프로그램을 종료합니다")
