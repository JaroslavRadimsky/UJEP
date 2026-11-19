options(width = 100)
source_file <- "penguins.csv"
source_hash <- unname(tools::md5sum(source_file))
penguins <- read.csv(source_file, na.strings = "NA", stringsAsFactors = FALSE)
original <- penguins
cat(R.version.string, "\n")
print(head(penguins, 6), row.names = FALSE)
cat("Dimensions:", dim(penguins), "\n")
print(vapply(penguins, function(x) paste(class(x), collapse = "/"), character(1)))
str(penguins)
print(colSums(is.na(penguins)))
stopifnot(identical(dim(penguins), c(344L, 8L)))
cat("PASS: 344 rows, 8 columns\n")

cols <- c("species", "island", "flipper_length_mm")
selected <- penguins[, cols, drop = FALSE]
vector <- penguins[["flipper_length_mm"]]
one_column <- penguins[, "flipper_length_mm", drop = FALSE]
cat("Selection:", dim(selected), "\n")
cat("1D:", class(vector), "typeof:", typeof(vector), "length:", length(vector), "\n")
cat("Table:", class(one_column), "dim:", dim(one_column), "\n")
positions <- selected[5:10, , drop = FALSE]
print(positions, row.names = FALSE)
stopifnot(identical(dim(selected), c(344L, 3L)),
          identical(dim(positions), c(6L, 3L)), length(vector) == 344L,
          identical(dim(one_column), c(344L, 1L)))
small <- head(selected, 6)
rownames(small) <- sprintf("p%02d", 1:6)
stopifnot(!anyDuplicated(rownames(small)))
print(small[c("p02", "p05"), , drop = FALSE])
reverse <- small[6:1, , drop = FALSE]
print(reverse)
cat("First row by position:\n")
print(reverse[1, , drop = FALSE])
cat("p01 by label:\n")
print(reverse["p01", , drop = FALSE])
stopifnot(rownames(reverse)[1] == "p06",
          identical(reverse["p01", , drop = FALSE], small["p01", , drop = FALSE]))
cat("PASS: dimensions, unique labels and selections\n")

mask1 <- !is.na(penguins$flipper_length_mm) & (penguins$flipper_length_mm >= 210)
mask2 <- (penguins$species == "Gentoo") & !is.na(penguins$body_mass_g) &
         (penguins$body_mass_g >= 5000)
mask3 <- ((penguins$island == "Biscoe") | (penguins$island == "Dream")) &
         !is.na(penguins$bill_length_mm) & (penguins$bill_length_mm < 45)
f1 <- penguins[mask1, , drop = FALSE]
f2 <- penguins[mask2, , drop = FALSE]
f3 <- penguins[mask3, , drop = FALSE]
cat("F1 count:", nrow(f1), "\n")
print(head(f1[, c("species", "island", "flipper_length_mm")], 10), row.names = FALSE)
cat("F2 count:", nrow(f2), "\n")
print(head(f2[, c("species", "body_mass_g")], 10), row.names = FALSE)
cat("F3 count:", nrow(f3), "\n")
print(head(f3[, c("island", "bill_length_mm")], 10), row.names = FALSE)
stopifnot(all(!is.na(f1$flipper_length_mm)), all(f1$flipper_length_mm >= 210),
          all(f2$species == "Gentoo"), all(!is.na(f2$body_mass_g)),
          all(f2$body_mass_g >= 5000), all(f3$island %in% c("Biscoe", "Dream")),
          all(!is.na(f3$bill_length_mm)), all(f3$bill_length_mm < 45))
filter_counts <- c(nrow(f1), nrow(f2), nrow(f3))
cat("PASS: every retained row meets the conditions:", filter_counts, "\n")

mass_mask <- penguins$body_mass_g >= 5000
direct <- penguins[mass_mask, , drop = FALSE]
via_subset <- subset(penguins, body_mass_g >= 5000)
correct_mask <- !is.na(mass_mask) & mass_mask
corrected <- penguins[correct_mask, , drop = FALSE]
unknown_rows <- rowSums(is.na(direct)) == ncol(direct)
cat("NA entries in the mask:", sum(is.na(mass_mask)), "\n")
cat("Direct indexing:", nrow(direct), "; all-NA rows:", sum(unknown_rows), "\n")
print(direct[unknown_rows, , drop = FALSE])
cat("subset:", nrow(via_subset), "; corrected mask:", nrow(corrected), "\n")
stopifnot(!anyNA(correct_mask), identical(corrected, via_subset),
          nrow(direct) == nrow(corrected) + sum(is.na(mass_mask)))
cat("PASS: the explicitly corrected mask matches subset()\n")

working <- penguins[, c("species", "island", "flipper_length_mm", "body_mass_g")]
working$body_mass_kg <- working$body_mass_g / 1000
ord <- order(working$species, -working$body_mass_g, seq_len(nrow(working)),
             na.last = TRUE, method = "radix")
working <- working[ord, , drop = FALSE]
rownames(working) <- NULL
print(head(working, 10), row.names = FALSE)
known <- !is.na(working$body_mass_g)
stopifnot(all(abs(working$body_mass_kg[known] - working$body_mass_g[known]/1000) < 1e-12),
          nrow(working) == nrow(penguins),
          sum(is.na(working$body_mass_g)) == sum(is.na(penguins$body_mass_g)),
          ncol(penguins) == 8L, ncol(working) == 5L,
          identical(working$species, sort(working$species)), identical(penguins, original))
for (sp in unique(working$species)) {
    masses <- working$body_mass_g[working$species == sp]
    stopifnot(all(diff(masses[!is.na(masses)]) <= 0),
              all(diff(as.integer(is.na(masses))) >= 0))
}
cat("PASS: conversion (tol=1e-12), sorting, 344 rows, 5 columns,",
    sum(is.na(working$body_mass_g)), "missing masses; original unchanged\n")

verify_restored <- function(restored) {
    cat("Dimensions:", dim(restored), "\n")
    print(vapply(restored, class, character(1)))
    print(colSums(is.na(restored)))
    stopifnot(identical(dim(restored), dim(working)),
              identical(names(restored), names(working)),
              identical(is.na(restored), is.na(working)))
    for (column in names(working)) {
        if (is.numeric(working[[column]])) {
            stopifnot(is.numeric(restored[[column]]))
            known <- !is.na(working[[column]])
            stopifnot(all(abs(working[[column]][known] - restored[[column]][known]) < 1e-12))
        } else {
            stopifnot(identical(working[[column]], restored[[column]]))
        }
    }
    stopifnot(identical(vapply(restored, class, character(1)),
                        vapply(working, class, character(1))))
    cat("PASS: dimensions, names, types, missing values and all values\n")
}
write.csv(working, "working_r.csv", row.names = FALSE, na = "NA")
restored <- read.csv("working_r.csv", na.strings = "NA", stringsAsFactors = FALSE)
verify_restored(restored)
write.table(working, "working_r_semicolon.csv", sep = ";", dec = ",",
            row.names = FALSE, col.names = TRUE, na = "NA")
restored_semicolon <- read.table("working_r_semicolon.csv", header = TRUE,
    sep = ";", dec = ",", na.strings = "NA", stringsAsFactors = FALSE)
verify_restored(restored_semicolon)

tryCatch({
    wrong <- read.csv("working_r_semicolon.csv")
    cat("Incorrect import - dimensions:", dim(wrong), "\n")
    print(names(wrong))
    print(head(wrong, 3))
    stopifnot(!identical(dim(wrong), dim(working)) || !identical(names(wrong), names(working)))
}, error = function(e) cat("Expected import error:", conditionMessage(e), "\n"))
# Corrected import with the matching separator and decimal comma.
corrected_import <- read.table("working_r_semicolon.csv", header = TRUE,
    sep = ";", dec = ",", na.strings = "NA", stringsAsFactors = FALSE)
verify_restored(corrected_import)
stopifnot(identical(unname(tools::md5sum(source_file)), source_hash),
          identical(penguins, original))
cat("PASS: the source CSV and penguins object are unchanged\n")
cat("Filter counts:", filter_counts, "\n")
