from ingestion.text_cleaner import TextCleaner

cleaner = TextCleaner()

dirty = "Hello   world.\n\n\n\nPage 3 of 47\n12\nReal content here."

print(cleaner.clean(dirty))