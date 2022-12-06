# Changes

## 1.1.0 (unreleased)

### Changes
- Add NcML backend for `header` processor, allowing global metadata to be parsed from the THREDDS NCML service, or the 
  `ncdump -xh` command.
- Add intake-esm output plugging. Creates a `json` catalog description and `csv.gz` metadata table.
- Add `stac_generator.plugins.outputs.stacapi_backend:StacApiOutputBackend`.
- Remove `decode_times=False` from xarray backend dataset initialization.

### Fixes
- Correct naming of `stac_generator.plugins.extraction_methods.header_extract` to 
  `stac_generator.plugins.extraction_methods.header` to fit path structure.
- Add generator properties to `item["body"]["properties"]` instead of `item["body"]`.
- Make sure that `collection_description.id` and `item_description.id` exist before accessing these fields.
- Fix hashing function refering to standard library instead of `hashlib`.
- Fix entrypoints access in the `header` extractor.
- Fix `stac_generator.plugins.extraction_methods.json_file` undefined field access error.
