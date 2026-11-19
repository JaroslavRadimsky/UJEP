rm(list=ls())

# Shlukova analýza
## Použijte číselné proměnné z datovéhosouboru fgl z knihovny MASS.
library(MASS)
data("fgl")
help(fgl)

# Hierarchické shlukování
dist_matrix <- dist(fgl[, -10]) # Vypočítání vzdálenostní matice (bez posledního sloupce)

## Wardova metoda
hc.ward <- hclust(dist_matrix, method = "ward.D2")
plot(hc.ward, main = "Dendrogram")
rect.hclust(hc.ward, k = 6, border = "red") # Zvýraznění 6 shluků
clusters.ward <- cutree(hc.ward, k = 6)
table(clusters.ward, fgl$type) # Porovnání s původními typy

## Complete linkage
hc.complete <- hclust(dist_matrix, method = "complete")
plot(hc.complete, main = "Dendrogram")
rect.hclust(hc.complete, k = 6, border = "orange") # Zvýraznění 6 shluků
clusters.comp <- cutree(hc.complete, k = 6)
table(clusters.comp, fgl$type) # Porovnání s původními typy
  # mimo

## Average linkage
hc.average <- hclust(dist_matrix, method = "average")
plot(hc.average, main = "Dendrogram")
rect.hclust(hc.average, k = 6, border = "blue") # Zvýraznění 6 shluků
clusters.avg <- cutree(hc.average, k = 6)
table(clusters.avg, fgl$type) # Porovnání s původními typy
  # uplně mimo

## Single linkage
hc.single <- hclust(dist_matrix, method = "single")
plot(hc.single, main = "Dendrogram")
rect.hclust(hc.single, k = 6, border = "green") # Zvýraznění 6 shluků
clusters.single <- cutree(hc.single, k = 6)
table(clusters.single, fgl$type) # Porovnání s původními typy
  # uplně mimo




# K-means shlukování
km <- kmeans(fgl[, -10], centers = 6, nstart = 25)
table(km$cluster, fgl$type) # Porovnání s původními typy

# standardizace dat
fgl_scaled <- scale(fgl[, -10])
km_scaled <- kmeans(fgl_scaled, centers = 6, nstart = 25)
table(km_scaled$cluster, fgl$type) # Porovnání s původními typy


##############################x

# Lineární regrese
## V datovém souboru Cars93 z knihovny MASS zjistěte, na čem závisí cena vozu (proměnná Price).
## Uvažujte pouze proměnné Type, MPG.city, MPG.highway, AirBags, Horsepower, RPM, Passengers, Length a Origin
library(car)


data("Cars93")
help(Cars93)

lm1 <- lm(Price ~ Type + MPG.city + MPG.highway + AirBags + Horsepower + RPM + Passengers + Length + Origin, data = Cars93)
summary(lm1)
Anova(lm1)
# Význemné proměnné jsou: AirBags, Horsepower a Origin



par(mfrow=c(2,2))
plot(lm1)
par(mfrow=c(1,1))

# Testování normality reziduí
shapiro.test(lm1$residuals) # p < 0,05 -> nejsou normálně rozdělené

# Testování homoskedasticity
ncvTest(lm1) # p < 0.05 -> heteroskedasticita (nemáme konstantní rozptyl)

# Testování multikolinearity
cor(Cars93[, c("MPG.city", "MPG.highway", "Horsepower", "RPM", "Passengers", "Length")])

# Vysoká korelace mezi MPG.city a MPG.highway
corrplot::corrplot(cor(Cars93[, c("MPG.city", "MPG.highway", "Horsepower", "RPM", "Passengers", "Length")]), method = "circle")

# Boxplot jednotlitvhy promennych
par(mfrow=c(2,5))
boxplot(Cars93$Price, main="Price")
boxplot(Cars93$MPG.city, main="MPG.city")
boxplot(Cars93$MPG.highway, main="MPG.highway")
boxplot(Cars93$Horsepower, main="Horsepower")
boxplot(Cars93$RPM, main="RPM")
boxplot(Cars93$Passengers, main="Passengers")
boxplot(Cars93$Length, main="Length")
boxplot(Cars93$Type, main="Type")
boxplot(Cars93$AirBags, main="AirBags")
boxplot(Cars93$Origin, main="Origin")
par(mfrow=c(1,1))


# Kroková regrese
lm.step <- step(lm1)
summary(lm.step)

par(mfrow=c(2,2))
plot(lm.step)
par(mfrow=c(1,1))

shapiro.test(lm.step$residuals)
ncvTest(lm.step)
