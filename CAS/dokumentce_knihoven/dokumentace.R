# import knihovny
library(alphavantager)

# je potřeba získat API key z: https://www.alphavantage.co/support/#api-key

# nastavení API key pomocí av_api_key("YOUR_API_KEY")
av_api_key(Sys.getenv("ALPHAVANTAGE_API_KEY"))

# získání dat pomocí funkce av_get()
av_data <- av_get(symbol = "MSFT", av_fun = "TIME_SERIES_INTRADAY", interval = "15min", outputsize = "full")


#######################

library(Quandl)

# pro API key je potřeba vytvořit účet na https://data.nasdaq.com/sign-up

# nastavení API key pomocí Quandl.api_key("YOUR_API_KEY")
Quandl.api_key(Sys.getenv("QUANDL_API_KEY"))

# získání dat pomocí funkce Quandl.datatable()
quandl_bitcoin <- Quandl.datatable('QDL/BCHAIN', code='TVTVR')

# datasety lze hledat na https://data.nasdaq.com/search
# zdarma je dostupných pouze 9 datových sad!!


