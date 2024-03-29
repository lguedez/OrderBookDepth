import binance 
import websocket
import json
import requests
import time
import pandas as pd
from datetime import datetime
import threading
import matplotlib.pyplot as plt 


class Exchange():
#---------------------- Atributos ----------------------------------------
    # local data management

#--------------------- Constructores ----------------------------------------
    def __init__(self,simbolos,tiempo):
        # create websocket connection
        #1. Open a stream to wss://stream.binance.com:9443/ws/ParMonedas@depth
        self.ws = websocket.create_connection("wss://stream.binance.com:9443/ws/"+simbolos.lower()+"@depth")
        # local data management
        self.orderbook = {}
        self.updates = 0
        self.tiempo = tiempo
        self.simbolos = simbolos
#--------------------- Metodos ----------------------------------------
        # catch errors
    def on_error(self, error):
        print(error)

    # run when websocket is closed
    def on_close(self):
        print("### closed ###")

    # run when websocket is initialised
    def on_open(self):
        print('Connected to Binance\n')
        self.get_snapshot()

        # retrieve orderbook snapshot
    def get_snapshot(self):
        #3. Get a depth snapshot from https://api.binance.com/api/v3/depth?symbol=ParMonedas&limit=1000
        r = requests.get("https://api.binance.com/api/v3/depth?symbol="+simbolos.upper()+"&limit=1000")
        depthsnapshot = r.json()
        self.orderbook = depthsnapshot
        return depthsnapshot

        # convert message to dict, process update
    def on_message(self):
        #2. Buffer the events you receive from the stream
        start_time = time.time()
        while (time.time() - start_time) < tiempo:
            message=self.ws.recv()
            data = json.loads(message)
            #print(data)
            # check for orderbook, if empty retrieve
            if len(self.orderbook) == 0:
                self.orderbook = self.get_snapshot()

            # get lastUpdateId
            lastUpdateId = self.orderbook['lastUpdateId']

            # drop any updates older than the snapshot
            #5. The first processed event should have U <= lastUpdateId+1 AND u >= lastUpdateId+1
            if self.updates == 0:
                if data['U'] <= lastUpdateId+1 and data['u'] >= lastUpdateId+1:
                    print(f'lastUpdateId {data["u"]}')
                    self.orderbook['lastUpdateId'] = data['u']
                    self.process_updates(data)
                else:
                    print('discard update')
            
            # check if update still in sync with orderbook
            elif data['U'] == lastUpdateId+1:
                print(f'lastUpdateId {data["u"]}')
                self.orderbook['lastUpdateId'] = data['u']
                self.process_updates(data)
            else:
                print('Out of sync, abort')

    # Loop through all bid and ask updates, call manage_orderbook accordingly
    def process_updates(self, data):
        for update in data['b']:
            self.manage_orderbook('bids', update)
        for update in data['a']:
            self.manage_orderbook('asks', update)
        print()

    # Update orderbook, differentiate between remove, update and new
    def manage_orderbook(self, side, update):
        # extract values
        price, qty = update
        qty=float (qty)
        price=float (price)
        # loop through orderbook side
        for x in range(0, len(self.orderbook[side])):
            if price == float (self.orderbook[side][x][0]):
                # when qty is 0 remove from orderbook, else
                # update values
                if qty == 0:
                    del self.orderbook[side][x]
                    print(f'Removed {side} {price} {qty}')
                    break
                else:
                    self.orderbook[side][x] = update
                    print(f'Updated: {side} {price} {qty}')
                    break
            # if the price level is not in the orderbook, 
            # insert price level, filter for qty 0
            elif price != float (self.orderbook[side][x][0]):
                if qty != 0:
                    self.orderbook[side].insert(x, update)
                    print(f'New price: {side} {price} {qty}')
                    break
                else:
                    break

#--------------------- Aqui comienza el programa principal ----------------------------------------
if __name__ == "__main__":
    simbolos="ETHUSDT"
    tiempo=69 # tiempo en segundos
    cliente=Exchange(simbolos,tiempo)# creo el objeto
    cliente.on_open()
    cliente.on_message()
    cliente.on_close()

    client = binance.Client()
    order_book = cliente.orderbook   
    bids = pd.DataFrame(order_book['bids'])
    asks = pd.DataFrame(order_book['asks'])

    #print(bids.info())
    #Convierto en numeros precio y cantidad
    
    bids[1] = pd.to_numeric(bids[1])
    bids[0] = pd.to_numeric(bids[0])
    asks[1] = pd.to_numeric(asks[1])
    asks[0] = pd.to_numeric(asks[0])

    #-----------precios-------------------
    ask_Pminimo = min(asks.iloc[:,0])
    ask_Pmaximo = max(asks.iloc[:,0])
    bid_Pmaximo = max(bids.iloc[:,0])
    bid_Pminimo = min(bids.iloc[:,0])

    ask_min = ask_Pminimo
    bid_max = bid_Pmaximo
    q_b = bids[1]
    q_a = asks[1]
    p_b = bids[0]
    p_a = asks[0]


    #Ordeno de forma decendente por cantidad
    bids = bids.groupby([0]).mean([1])
    asks = asks.groupby([0]).mean([1])
    bids.sort_values(by=1, ascending=False, inplace=True)
    asks.sort_values(by=1, ascending=False, inplace=True)
    print('\nOrdenados Por Cantidad')
    print('\nTop 20 valores de Venta Asks\n')
    asks10=asks.head(20)
    print(asks10)
    print('\nTop 20 valores de Compra Bids')
    bids10=bids.head(20)
    print(bids10)
    print('\nOrdenados Por Precio\n')
    print('\nTop 10 Precios valores de Venta Asks')
    print(asks10.sort_values(by=0, ascending=False, inplace=False))
    print('\nTop 10 Precios valores de Compra Bids')
    print(bids10.sort_values(by=0, ascending=False, inplace=False))

   
    
    # Abrir un archivo JSON
    json_file = open("C:\leo\leo.json", "w")
    # Crear un diccionario con los datos
    datos = {'datos': 'valor'}
    # Convertir el diccionario a una cadena de texto
    json_string = json.dumps(order_book)
    # Escribir la cadena JSON en el archivo abierto
    json_file.write(json_string)
    # Cerrar el archivo
    json_file.close()
    
    price_now = client.futures_mark_price(symbol =  simbolos )
    price = float(price_now['markPrice'])
    print('Finalizo programa\n')

