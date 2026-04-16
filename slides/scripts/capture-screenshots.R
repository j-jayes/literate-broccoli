# Regenerate README screenshots for the rendered RevealJS deck.
#
# Prerequisites:
# - Quarto rendered `template.html`
# - R package `webshot2`
# - A Chromium-based browser available to Chromote/Webshot2

if (!requireNamespace("webshot2", quietly = TRUE)) {
  stop(
    "The 'webshot2' package is required. Install it with install.packages('webshot2').",
    call. = FALSE
  )
}

root <- normalizePath(file.path(getwd()), winslash = "/", mustWork = TRUE)
input <- normalizePath(file.path(root, "template.html"), winslash = "/", mustWork = TRUE)
output_dir <- file.path(root, "assets", "screenshots")

if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
}

slides <- list(
  list(hash = "#/title-slide", file = "title-slide.png"),
  list(hash = "#/built-for-clear-narrative-not-decorative-noise", file = "system-slide.png"),
  list(hash = "#/image-led-storytelling-without-clutter", file = "image-slide.png")
)

for (slide in slides) {
  url <- paste0("file:///", input, slide$hash)
  output <- file.path(output_dir, slide$file)

  webshot2::webshot(
    url = url,
    file = output,
    vwidth = 1600,
    vheight = 900,
    cliprect = "viewport",
    delay = 1.5
  )
}

message("Saved screenshots to: ", normalizePath(output_dir, winslash = "/", mustWork = TRUE))