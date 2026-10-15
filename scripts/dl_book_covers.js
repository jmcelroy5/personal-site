#!/usr/bin/env node
import fs from "fs";
import path from "path";
import axios from "axios";
import yaml from "js-yaml";

const INPUT_FILE = "_data/books.yml";
const OUTPUT_DIR = "assets/images/book-covers";

async function main() {
  const fileContents = fs.readFileSync(INPUT_FILE, "utf8");
  const books = yaml.load(fileContents);
  let notFoundCount = 0;
  let isbnMissingCount = 0;

  for (const book of books) {
    const { title, isbn13, isbn } = book;
    const outputPath = path.join(OUTPUT_DIR, `${isbn13}.jpg`);

    if (fs.existsSync(outputPath)) {
      continue;
    }

    const urlsToTry = []
    if (isbn13) {
      urlsToTry.push(`https://covers.openlibrary.org/b/isbn/${isbn13}-M.jpg`)
      urlsToTry.push(`https://covers.openlibrary.org/b/isbn/${isbn13}-L.jpg`)
    }
    if (isbn) {
      urlsToTry.push(`https://covers.openlibrary.org/b/isbn/${isbn}-M.jpg`)
      urlsToTry.push(`https://covers.openlibrary.org/b/isbn/${isbn}-L.jpg`)
    }
    if (!urlsToTry.length) {
      isbnMissingCount++
      console.log(`❌ No isbn present for "${title}"`);
      continue;
    }

    let success = false;
    for (const url of urlsToTry) {
      try {
        const response = await axios.get(url, { responseType: "arraybuffer" });

        // The Open Library API returns a 1x1 transparent image if cover not found.
        if (response.headers["content-length"] === "0" || response.data.length < 500) {
          continue;
        } else {
          fs.writeFileSync(outputPath, response.data);
          console.log(`✅ Found! Saved to ${outputPath}`);
          success = true;
          break;
        }
      } catch (err) {
        console.log(`⚠️ Error on download "${title}" at ${url}: ${err.message}`);
      }
    }

    if (!success) {
      notFoundCount++;
      console.log(`❌ ${title}, file path: ${outputPath}`);
    }
  }
  console.log(`Done! notFoundCount: ${notFoundCount}, isbnMissingCount: ${isbnMissingCount}`);
}

main();
