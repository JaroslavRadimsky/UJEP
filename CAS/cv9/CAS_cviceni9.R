############################
library(forecast)
library(dynlm)
library(lmtest)
library(TSA)
# nacteni knihoven

############################
data("M1Germany")
head(M1Germany)
  # ekonomicka ctvrtletni data z Nemecka
  # M1 index "financni zasoby"

plot(M1Germany)
  # ctyri casove rady, kdy nas zajima, jaky je vztah mezi logm1 a ostatnimi

# Crosskorelacni funkce
par(mfrow = c(3,1))
ccf(M1Germany$logm1, M1Germany$logprice, na.action = na.pass)
ccf(M1Germany$logm1, M1Germany$loggnp, na.action = na.pass)
ccf(M1Germany$logm1, M1Germany$interest, na.action = na.pass)
par(mfrow = c(1,1))
  # je videt vysoka korelovanost s ostatnimi radami
  # s logprice a loggnp s nulovym zpozdenim
  # s interest se zpozdenim 4 roky

# regresni modely
fit1 <- dynlm(M1Germany$logm1 ~ M1Germany$logprice + M1Germany$loggnp + M1Germany$interest)
  # zavislost v aktualnim case
summary(fit1)
  # shrnuti modelu
# ale neni lepsi brat i promenne interest zavislost se zpozdenim?
fit2 <- dynlm(M1Germany$logm1 ~ M1Germany$logprice + M1Germany$loggnp + L(M1Germany$interest, -16))
  # zpozdena zavislost o 4 kroky na Interest
summary(fit2)
  # zavislost na interest se zde neprojevila

acf(fit1$residuals)
  # mam korelovana residua, musim pridat jeste cast arima 
  #   nebo zavislost na vlastnich zpozdenych pozorovanich

fit3 <- dynlm(M1Germany$logm1 ~ M1Germany$logprice + M1Germany$loggnp + M1Germany$interest + 
                L(M1Germany$logm1, 1))
summary(fit3)
acf(fit3$residuals)
  # zavislost na minule hodnote

fit4 <- dynlm(M1Germany$logm1 ~ M1Germany$logprice + M1Germany$loggnp + M1Germany$interest + 
                L(M1Germany$logm1, 4))
summary(fit4)
acf(fit4$residuals)
  # zavislost o jednu sezonu zpet dava lepsi vysledky

fit5 <- dynlm(M1Germany$logm1 ~ M1Germany$logprice + M1Germany$loggnp + M1Germany$interest + 
                L(M1Germany$logm1, 1) + L(M1Germany$logm1, 4))
summary(fit5)
acf(fit5$residuals)
  # zavislost o jednu sezonu i na minule hodnote
  # autokorelovanost residui se tim prilis nevyresila - bude lepsi sahnout k ARMA modelum pro residua

# vytvoreni matice regresoru
x.reg <- as.matrix(M1Germany[,2:4])
fit6 <- auto.arima(M1Germany$logm1, xreg = x.reg)
summary(fit6)
  # residua se ridi ARMA procesem az na prvnich sezonnich diferencich
coeftest(fit6)
  # vsechny koeficienty modelu jsou vyznamne
acf(fit6$residuals, na.action = na.pass)
  # nekorelovana residua - dobry model
checkresiduals(fit6)

# jak model sedi na data
figure <- ts.intersect(M1Germany$logm1, fitted(fit6))
plot.ts(figure, plot.type = "single", col=c("black","red"), 
        lty=c(1,1), lwd=c(1,1),
        main = "'Classic' Linear Model - Original (black) and Fitted series (red)") 

# pokud budu chtit predikovat bez znalosti jinych rad, tento model mi prilis nepomuze
# samostatna auto arima
fit7 <- auto.arima(M1Germany$logm1)
summary(fit7)
coeftest(fit7)
acf(fit7$residuals, na.action = na.pass)
  # nekorelovana residua - dobry model

# jak model sedi na data
figure <- ts.intersect(M1Germany$logm1, fitted(fit7))
plot.ts(figure, plot.type = "single", col=c("black","red"), 
        lty=c(1,1), lwd=c(1,1),
        main = "'Classic' Linear Model - Original (black) and Fitted series (red)") 

# ktery model je lepsi?
BIC(fit6)
BIC(fit7)
  # model s regresory je lepsi

BIC(fit5)
  # dynamicky model s korelovanymi residui

# predpovedi pro model fit7
for7 <-forecast(fit7)
plot(for7)
for7
  # vykresleni a vypsani predpovedi s intervaly spolehlivosti

#############################
### Samostatne

# pouzijte databazi EuStockMarkets a zkuste najit optimalni model pro index DAX
  # databaze burzovnich indexu
plot(EuStockMarkets)
stocks <- as.data.frame(EuStockMarkets)
View(stocks)

# Crosskorelacni funkce
par(mfrow = c(3,1))
ccf(stocks$DAX, stocks$CAC, na.action = na.pass)
ccf(stocks$DAX, stocks$SMI, na.action = na.pass)
ccf(stocks$DAX, stocks$FTSE, na.action = na.pass)
par(mfrow = c(1,1))
  # je videt vysoka korelovanost s ostatnimi radami

# regresni modely
fit1 <- dynlm(stocks$DAX ~ stocks$CAC + stocks$SMI + stocks$FTSE)

summary(fit1)
acf(fit1$residuals)

fit1.2 <- dynlm(stocks$DAX ~ stocks$CAC + stocks$SMI + stocks$FTSE + L(stocks$DAX, 1))
summary(fit1.2)
acf(fit1.2$residuals)

fit1.3 <- dynlm(stocks$DAX ~ stocks$CAC + stocks$SMI + L(stocks$DAX, 1))
summary(fit1.3)
acf(fit1.3$residuals)

# vytvoreni matice regresoru
x.reg <- as.matrix(stocks[,2:4])
fit2 <- auto.arima(stocks$DAX, xreg = x.reg)
summary(fit2)
coeftest(fit2)
acf(fit2$residuals, na.action = na.pass)
checkresiduals(fit2)

fit3 <- auto.arima(stocks$DAX)
summary(fit3)
coeftest(fit3)
acf(fit3$residuals, na.action = na.pass)
checkresiduals(fit3)

BIC(fit1)
BIC(fit1.2)
BIC(fit1.3)
BIC(fit2)
BIC(fit3)

fitted_ts <- ts(fitted(fit1.3), start = start(stocks$DAX), frequency = frequency(stocks$DAX))
figure <- ts.intersect(stocks$DAX, fitted_ts)
plot.ts(figure, plot.type = "single", col=c("black","red"), 
        lty=c(1,1), lwd=c(1,1),
        main = "'Classic' Linear Model - Original (black) and Fitted series (red)")

fitted_ts <- ts(fitted(fit1.3), start = start(stocks$DAX), frequency = frequency(stocks$DAX))
figure <- ts.intersect(stocks$DAX, fitted_ts)
plot.ts(figure, plot.type = "single", col=c("black","red"), 
        lty=c(1,1), lwd=c(1,1),
        main = "'auto.arima with regressors' - Original (black) and Fitted series (red)")



# nactete data EMG a hledejte optimalni model pro radu iEMG
#############################
## periodogram - hledani cyklu
plot(lynx)
  # data s evidentnimi cykly, ale nejedna se o sezonni data

n <- length(lynx)
FF <- abs(fft(lynx)/sqrt(n))^2
  # Fast Discrete Fourier Transform
P <- (4/n)*FF[1:(n/2 + 1)] 
  # potrebujeme prvnich (n/2)+1 hodnot FFT transformace
P <- P[-1]
  # prvni hodnota je nesmzslna

f <- (0:(n/2))/n 
  # this creates harmonic frequencies from 0 to .5 in steps of 1/n.
f <- f[-1]
plot(f, P, type="l")
  # periodogram rucne
(fr.max <- f[which.max(P)])
  # frekvence s maximalni hodnotou periodogramu
1/fr.max

per <- periodogram(lynx)
abline(h=0)

per$freq
per$spec
(fr.max <- per$freq[which.max(per$spec)])
  # frekvence s maximalni hodnotou periodogramu
1/fr.max
  # delka cyklu

############################
### Samostatne 

# hledejte delku cyklu pro slunecni aktivitu
data("sunspots")
  # mesicni data
plot(sunspots)


n <- length(sunspots)
FF <- abs(fft(sunspots)/sqrt(n))^2
  # Fast Discrete Fourier Transform
P <- (4/n)*FF[1:(n/2 + 1)]
  # potrebujeme prvnich (n/2)+1 hodnot FFT transformace
P <- P[-1]
  # prvni hodnota je nesmzslna
f <- (0:(n/2))/n
  # this creates harmonic frequencies from 0 to .5 in steps of 1/n.
f <- f[-1]
plot(f, P, type="l")
  # periodogram rucne
(fr.max <- f[which.max(P)])
  # frekvence s maximalni hodnotou periodogramu
1/fr.max
per <- periodogram(sunspots)
abline(h=0)
per$freq
per$spec
(fr.max <- per$freq[which.max(per$spec)])
  # frekvence s maximalni hodnotou periodogramu
1/fr.max
  # delka cyklu (v mesicich)
1/fr.max/12
  # delka cyklu (v letech)

# druhy cyklus (druhy nejvyssi vrchol v periodogramu)
library(TSA)      # kvůli periodogram()
library(zoo)      # pro rollapply

data("sunspots")

# Vygeneruj periodogram
per <- periodogram(sunspots, plot = FALSE)

# Získání frekvencí a spektra
f <- per$freq
P <- per$spec

# Najdeme index hlavního vrcholu
main_peak_idx <- which.max(P)

# Najdeme všechna lokální maxima (v okně délky 3)
is_local_max <- function(x) which(x == max(x) & x > x[1] & x > x[3])
local_max_idx <- rollapply(P, width = 3, FUN = is_local_max, by = 1, align = "center", partial = TRUE)
local_max_idx <- which(!is.na(local_max_idx))

# Vynecháme hlavní vrchol a jeho blízké okolí (např. ±10 indexů)
filtered_idx <- local_max_idx[abs(local_max_idx - main_peak_idx) > 10]

# Najdeme druhý nejvyšší vrchol z filtrovaných lokálních maxim
second_peak_idx <- filtered_idx[which.max(P[filtered_idx])]

# Výsledky
second_freq <- f[second_peak_idx]
second_period_months <- 1 / second_freq
second_period_years <- second_period_months / 12

cat("Druhý cyklus:\n")
cat("Frekvence:", second_freq, "\n")
cat("Perioda v měsících:", second_period_months, "\n")
cat("Perioda v letech:", second_period_years, "\n")





