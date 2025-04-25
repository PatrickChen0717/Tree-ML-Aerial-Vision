def score_reader(log_path, score_name):
    """Reads the performance scores"""
    
    with open(log_path) as f:
        content = f.readlines()
    
    # search each line for the string pattern of the "score_name"
    # for each line found to contain the "score_name", strip out the newline character
    # and the score_name from the string so that only the numeric score value remains
    scores = [float(line.strip(score_name).strip("\n")) for line in content 
              if score_name in line]
    
    return scores