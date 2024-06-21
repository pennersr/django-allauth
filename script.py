#used in open source projects to ensure smooth download from requirements.txt packages as sometimes it may not download very easily especially with a large number of packages.

def compare_pip_list_with_requirements(pip_list_output: str, requirements_file_path: str):
    
    pip_list_dict = {}
    for line in pip_list_output.strip().split('\n'):
        if line:
            package, version = line.split()
            pip_list_dict[package] = version
    
    
    with open(requirements_file_path, 'r') as f:
        requirements = f.readlines()
    
    missing_packages = []
    for requirement in requirements:
        if '==' in requirement:
            package, required_version = requirement.strip().split('==')
        else:
            package = requirement.strip()
            required_version = None
        
        if package not in pip_list_dict:
            if required_version:
                missing_packages.append(f"pip install {package}=={required_version}")
            else:
                missing_packages.append(f"pip install {package}")
        elif required_version and pip_list_dict[package] != required_version:
            missing_packages.append(f"pip install {package}=={required_version} (version mismatch: required {required_version}, found {pip_list_dict[package]})")
    
    return missing_packages


if __name__ == "__main__":
    print("Please paste your 'pip list' output below and then press Enter twice when done:")
    
    
    pip_list_output = ""
    while True:
        try:
            line = input()
            if line == "":
                break
            pip_list_output += line + "\n"
        except EOFError:
            break
    
    requirements_file_path = 'requirements.txt'
    missing_packages = compare_pip_list_with_requirements(pip_list_output, requirements_file_path)
    
    if missing_packages:
        print("Missing packages:")
        for package in missing_packages:
            print(package)
    else:
        print("All packages from requirements.txt are installed.")
