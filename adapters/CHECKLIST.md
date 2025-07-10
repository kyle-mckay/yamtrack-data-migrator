# Adapter Testing Checklist

This is a basic checklist to ensures that a data adapter correctly transforms and validates source data for compatibility with the target system.

---

## 🔧 Setup

- [ ] Confirm source file format matches expected schema (e.g., `.csv`, `.json`)
- [ ] Validate that required input files are present and accessible
- [ ] Verify adapter environment dependencies are installed (e.g., Python version, modules)
- [ ] Confirm configuration or mapping files are loaded properly (if applicable)

---

## 🔄 Data Transformation

- [ ] Column mappings align with expected source and destination schema
- [ ] All required fields are populated in the output
- [ ] Data types are preserved or converted as necessary (e.g., date strings → ISO8601)
- [ ] Optional/nullable fields are handled gracefully
- [ ] Default values are applied correctly where source data is missing

---

## 🧪 Functional Tests

- [ ] Run adapter on a **known-good sample** and compare output to expected results
- [ ] Run adapter on **edge case sample** (e.g., missing fields, extra whitespace)
- [ ] Test adapter with **malformed input** to confirm it fails gracefully
- [ ] Verify adapter skips or logs invalid rows without crashing
- [ ] Confirm that output is compatible with the target system (e.g., YamTrack import succeeds)

---

## 📁 Output Validation

- [ ] Output file is created in the correct format and location
- [ ] Output is parsable by the destination system (e.g., CSV loads without error)
- [ ] All rows are transformed correctly (manual spot check)
- [ ] Headers in the output file match the expected format

---

## 📜 Logging & Debugging

- [ ] Errors and warnings are logged to console or file
- [ ] Verbose or debug mode is available (if applicable)
- [ ] Adapter reports row-level processing issues (if possible)

---

## 🧹 Cleanup

- [ ] Temporary files (if any) are removed after processing
- [ ] Logs are stored or rotated according to policy
- [ ] Output files are timestamped or uniquely named to avoid overwriting

---

## ✅ Final Verification

- [ ] Review full output in the destination system to ensure data is usable
- [ ] Document any assumptions, limitations, or required manual steps
- [ ] Tag or version the adapter if releasing or deploying

