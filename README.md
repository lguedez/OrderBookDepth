# OrderBookDepth
Order Book Depth Binance Libro de Ordenes de Binance
El siguiente Codigo devuelve un libro ordenes de Binance.
como entradas se le debe dar el par de monedas ejemplo: BTCUSDT y el tiempo que se realizara el muestreo en segundos.
al final crea un archivo en la carpeta C:\Leo llamado leo.json que lo utilizo para analizar la data en excel. Si consigo varias estrellas compartire el excel.

El programa toma en cuenta lo indicado en la referencia de Binance https://binance-docs.github.io/apidocs/spot/en/#how-to-manage-a-local-order-book-correctly

"How to manage a local order book correctly
Open a stream to wss://stream.binance.com:9443/ws/bnbbtc@depth.
Buffer the events you receive from the stream.
Get a depth snapshot from https://api.binance.com/api/v3/depth?symbol=BNBBTC&limit=1000 .
Drop any event where u is <= lastUpdateId in the snapshot.
The first processed event should have U <= lastUpdateId+1 AND u >= lastUpdateId+1.
While listening to the stream, each new event's U should be equal to the previous event's u+1.
The data in each event is the absolute quantity for a price level.
If the quantity is 0, remove the price level.
Receiving an event that removes a price level that is not in your local order book can happen and is normal."
