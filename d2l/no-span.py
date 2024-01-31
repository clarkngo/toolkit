import re

def remove_span_tags_from_text(text):
    # Use regular expression to remove <span> tags
    cleaned_text = re.sub(r'<span.*?>|</span>', '', text)
    return cleaned_text

# Read content from input.txt
try:
    with open('input.txt', 'r') as file:
        input_text = file.read()
        result = remove_span_tags_from_text(input_text)
        
        # Save result to output.txt
        with open('output.txt', 'w') as output_file:
            output_file.write(result)
            
        print("Output after removing <span> tags saved to output.txt.")
except FileNotFoundError:
    print("Error: input.txt not found.")
