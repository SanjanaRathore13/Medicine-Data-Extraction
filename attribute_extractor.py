
import re


MONTHS = (
    r"JAN(?:UARY)?|FEB(?:RUARY)?|MAR(?:CH)?|APR(?:IL)?|"
    r"MAY|JUN(?:E)?|JUL(?:Y)?|AUG(?:UST)?|"
    r"SEP(?:T(?:EMBER)?)?|OCT(?:OBER)?|"
    r"NOV(?:EMBER)?|DEC(?:EMBER)?"
)

UNITS = r"mg|mcg|g|ml|iu"


def clean_value(value):
    value = re.sub(r"\s+", " ", value)
    return value.strip(" -_.,;:=|")


def normalize_text(text):
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[–—]", "-", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text


# 1. Medicine name




def extract_medicine_name(text):

    # Pattern 1: Brand name at the beginning
    match = re.search(
        r"^\s*([A-Za-z][A-Za-z0-9-]*)"
        r"[®©°*.\s-]*(\d{2,4})\b",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1) + " " + match.group(2)

    # Pattern 2: Brand followed by Tablets
    match = re.search(
        r"['‘\"]?([A-Za-z][A-Za-z0-9-]*)"
        r"['’\"]?\s*[®©°*.-]*\s*(\d{2,4})"
        r"\s*(?=Tablets?\b)",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1) + " " + match.group(2)

    # Pattern 3: Brand after strength
    match = re.search(
        r"\b\d+(?:\.\d+)?\s*mg\s+"
        r"([A-Za-z][A-Za-z0-9®*.-]*)"
        r"\s*[®©°*.-]*\s*(\d{2,4})",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1) + " " + match.group(2)

    # Pattern 4: Brand name on a separate line
    match = re.search(
        r"^\s*([A-Za-z][A-Za-z0-9-]*)\s+(\d{2,4})\s*$",
        text,
        re.MULTILINE
    )

    if match:
        return match.group(1) + " " + match.group(2)

    return None



# 2. Batch number

def extract_batch(text):

    match = re.search(
        r"\b(?:Batch\s*(?:No\.?|Number)?|B\s*\.?\s*No\.?)"
        r"\s*[:=\-]?\s*([A-Z0-9][A-Z0-9/-]{3,})",
        text,
        re.IGNORECASE
    )

    return match.group(1).upper() if match else None


# 3. Manufacturing and expiry dates


def extract_date(text, date_type):
    if date_type == "manufacturing":
        label = (
            r"\b(?:Mfg|Mfa|Mfd|Mfgd|Mig|"
            r"Manufacturing|Manufacture)"
            r"\s*\.?\s*Date\b")
    else:
        label = r"\b(?:Expiry|Exp|EXP)\s*\.?\s*Date?\b"


    date_pattern = rf"\b({MONTHS})\.?\s*[-:/]?\s*(20\d{{2}})\b"

    label_match = re.search(label, text, re.IGNORECASE)

    if not label_match:
        return None

    # First check after the date label
    after = text[label_match.end():label_match.end() + 100]

    date_match = re.search(
        date_pattern,
        after,
        re.IGNORECASE
    )

    if date_match:
        return (
            date_match.group(1).upper()
            + " "
            + date_match.group(2)
        )

    # If OCR has placed the date before its label,
    # check the nearby text before the label.
    if date_type == "manufacturing":
        before = text[max(0, label_match.start() - 100):label_match.start()]

        dates = list(re.finditer(
            date_pattern,
            before,
            re.IGNORECASE
        ))

        if dates:
            date_match = dates[-1]
            return (
                date_match.group(1).upper()
                + " "
                + date_match.group(2)
            )

    return None



# 4. MRP

def extract_mrp(text):

    patterns = [
        (
            r"\bM\s*\.?\s*R\s*\.?\s*P\s*\.?\s*"
            r"[^0-9]{0,30}"
            r"(\d{1,6}(?:\.\d{1,2})?)"
        )
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return float(match.group(1))

    return None



# 5. Strength

def extract_strength(text):

    matches = re.findall(
        rf"\b\d+(?:\.\d+)?\s*(?:{UNITS})\b",
        text,
        re.IGNORECASE
    )

    values = []

    for value in matches:
        value = re.sub(r"\s+", "", value.lower())

        if value not in values:
            values.append(value)

    return " + ".join(values) if values else None


# 6. Composition




def extract_composition(text):

    patterns = [
        # Pattern 1: Each tablet contains
        (
            r"\b(?:Each|E?ach)\s+"
            r"(?:(?:film\s+)?coated\s+|uncoated\s+)?"
            r"tablets?\s+contains\s*:?\s*"
            r"([\s\S]{1,350}?)"
            r"(?=\b(?:Batch|Dosage|Storage|"
            r"Mfg|Mig|Expiry|MRP)\b|$)"
        ),

        # Pattern 2: Composition label
        (
            r"\bComposition\s*:?\s*"
            r"([\s\S]{1,350}?)"
            r"(?=\b(?:Batch|Dosage|Storage|"
            r"Mfg|Mig|Expiry|MRP)\b|$)"
        ),

        # Pattern 3: Composition directly written in text
        # Pattern 3: Composition directly written in text
        (
            r"\b([A-Za-z]+\s+\d+(?:\.\d+)?\s*mg)"
            r"\s*\+\s*Tablets?\s*"
            r"([A-Za-z]+\s+\d+(?:\.\d+)?\s*mg)"
        )

    ]

    section = ""

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            section = (
                match.group(1) + " + " + match.group(2)
                if match.lastindex == 2
                else match.group(1)
                )
            break

    # Remove text after Equivalent to or Excipients
    section = re.split(
        r"\b(?:Equivalent\s+to|Excipients?|EXCIPIONES)\b",
        section,
        maxsplit=1,
        flags=re.IGNORECASE
    )[0]

    section = re.sub(r"\.{2,}", " ", section)

    section = re.sub(
        r"\b(?:Each|film|coated|uncoated|tablet|tablets|contains)\b",
        "",
        section,
        flags=re.IGNORECASE
    )

    section = re.sub(
        r"\b(?:IP|Be|ee)\b",
        "",
        section,
        flags=re.IGNORECASE
    )

    section = re.sub(r"[~_=]+", " ", section)

    section = clean_value(section)

    return section if re.search(r"[A-Za-z]", section) else None

# 7. Manufacturer

def extract_manufacturer(text):

    known_companies = [
        r"SunPharma\s+Laboratories\s+Ltd\.?",
        r"Alkem\s+Laboratories\s+Ltd\.?",
        r"Cipla\s+Ltd\.?"
    ]

    for pattern in known_companies:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return clean_value(match.group())

    match = re.search(
        r"Manufactured\s+by\s*[:= -]*"
        r"([\s\S]{0,100}?)"
        r"(?=\b(?:Expiry|Mfg|MRP|Batch|Store|Storage)\b|$)",
        text,
        re.IGNORECASE
    )

    if match:
        return clean_value(match.group(1))

    return None


# 8. Storage instructions


def extract_storage(text):

    match = re.search(
        r"\bStorage\s*:\s*"
        r"(.*?)"
        r"(?=\b(?:Dosage|Warning|Batch\s*No|"
        r"Mfg|Mig|Mfa|Mfd|Expiry|MRP|"
        r"Keep\s+out\s+of\s+reach|Manufactured\s+by)\b|$)",
        text,
        re.IGNORECASE
    )

    if not match:
        return None

    section = match.group(1)

    # Remove manufacturer names
    section = re.sub(
        r"\b(?:SunPharma\s+Laboratories\s+Ltd\.?|"
        r"Alkem\s+Laboratories\s+Ltd\.?|"
        r"Cipla\s+Ltd\.?)\b",
        " ",
        section,
        flags=re.IGNORECASE
    )

    # Remove address after company details
    section = re.split(
        r"\b(?:Plot\s+No\.?|Industrial\s+Area|"
        r"B-\d+|N-\d+|Sector-\d+)\b",
        section,
        maxsplit=1,
        flags=re.IGNORECASE
    )[0]

    section = re.sub(
        r"\b(?:aS|SS|ee)\b",
        " ",
        section,
        flags=re.IGNORECASE
    )

    section = clean_value(section)

    # Avoid repeated Store
    section = re.sub(
        r"^(?:Store\s+)+",
        "Store ",
        section,
        flags=re.IGNORECASE
    )

    return section if section else None


# 9. Extract all medicine attributes

def extract_medicine_details(text):

    text = normalize_text(text)

    return {
        "medicine_name": extract_medicine_name(text),
        "batch_no": extract_batch(text),
        "manufacturing_date": extract_date(text, "manufacturing"),
        "expiry_date": extract_date(text, "expiry"),
        "mrp": extract_mrp(text),
        "strength": extract_strength(text),
        "composition": extract_composition(text),
        "manufacturer": extract_manufacturer(text),
        "storage_instructions": extract_storage(text)
    }


# 10. Separate fixed and additional attributes

def extract_attributes(text):

    medicine = extract_medicine_details(text)

    fixed_fields = [
        "medicine_name",
        "batch_no",
        "manufacturing_date",
        "expiry_date",
        "mrp"
    ]

    fixed_attributes = {
        key: medicine.get(key)
        for key in fixed_fields
    }

    additional_attributes = {
        key: value
        for key, value in medicine.items()
        if key not in fixed_fields and value is not None
    }

    return {
        "fixed_attributes": fixed_attributes,
        "additional_attributes": additional_attributes
    }
