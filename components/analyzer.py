import re


def parse_abnormal_values(raw_text):
	"""
	Parse the structured abnormal values response from LLM
	into a list of dictionaries.
	"""
	blocks = re.findall(
		r'ABNORMAL_START(.*?)ABNORMAL_END',
		raw_text,
		re.DOTALL
	)

	results = []
	for block in blocks:
		data = {}
		for line in block.strip().split('\n'):
			if ':' in line:
				key, val = line.split(':', 1)
				data[key.strip()] = val.strip()
		if data:
			results.append(data)

	return results


def get_status_color(status):
	"""Return color based on HIGH/LOW status."""
	if status == "HIGH":
		return "#e74c3c", "🔴", "#fdf2f2"
	elif status == "LOW":
		return "#e67e22", "🟡", "#fef9f0"
	else:
		return "#27ae60", "🟢", "#f0fdf4"


def extract_key_metrics(pdf_text):
	"""
	Try to extract common blood test values directly
	from raw text using regex patterns.
	Used as a fallback display alongside AI analysis.
	"""
	metrics = {}

	patterns = {
		"Hemoglobin"   : r"[Hh]emoglobin[\s:]+([0-9.]+)\s*(g/dL|g/dl)?",
		"WBC"          : r"[Ww][Bb][Cc][\s:]+([0-9.]+)",
		"Platelets"    : r"[Pp]latelet[\s:]+([0-9.]+)",
		"RBC"          : r"[Rr][Bb][Cc][\s:]+([0-9.]+)",
		"Glucose"      : r"[Gg]lucose[\s:]+([0-9.]+)",
		"Creatinine"   : r"[Cc]reatinine[\s:]+([0-9.]+)",
		"Cholesterol"  : r"[Cc]holesterol[\s:]+([0-9.]+)",
	}

	for name, pattern in patterns.items():
		match = re.search(pattern, pdf_text)
		if match:
			metrics[name] = match.group(1)

	return metrics
