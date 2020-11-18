# MultiBL
Welcome to use our trustworthy bug localization tool with multi-language support.
## System requirement
* MacOS or Ubuntu
* JDK 1.8, for example:
    * java version "1.8.0_271"
    * Java(TM) SE Runtime Environment (build 1.8.0_271-b09)
    * Java HotSpot(TM) Server VM (build 25.271-b09, mixed mode)
* Python >= 3.7

## Format requirement

## Environment Configuration
Having conda installed on your machine, please execute `bash env_config.sh` to create a virtual environment and install necessary dependencies.

## Running Configuration
Make sure that you are in the root path of this repo. There should be `./result` folder in the repo, and the generated file will be stored in this folder.

### Configuring bug information

You need to specify bug information in `config.ini` file, including:
* repo_name: we set it as "HUAWEI"
* path_to_bug_report_sheet: path to the .xlsx that stores bug report information
* path_to_original_codebase: path to the codebase

### Configuring running mode
The tool runs in two mode:
* Optimistic filtering mode: generating buggy file recommendations for all bug report recieved;
* Conservative filtering mode: generating less recommendations, but recommendations are more trustworthy.

You can specify the mode in `config.ini`. You can also choose "all" to see the results of two modes at the same time.

### Configuring translation function
You can tell the tool whether you want translate the bug reports and comments in the codebase by specifying `is_translation_required` in `config.ini`.

[**PLEASE NOTE**]: The translation function is **NOT** implemented, since it can be risky to use translation service outside HUAWEI. Currently, the tool can run but translator only returns the original text. You want want to change `translator(text)` function (Line 125, in `translator.py`) to enable translating Chinese to English fuctionality.

## Running the tool
After you configuring environment and specifying necessary information, you can run the tool with `python multibl.py`
There are five steps:
* Step 0: converting .xlsx file into .xml file
* Step 1: Executing translation (if required)
* Step 2: Preprocessing bug reports, drops invalid ones
* Step 3: Localizing buggy files
* Step 4: Generating summary results

# System testing within SOAR
After you finishing the previous steps in MacOS, Ubuntu and Windows, you can execute `python test_multibl.py` (Only support MacOS and Linux), to see is there any exceptions raised. The programs will run in parallel and generate many messages. You may want to search for keyword, e.g. 'error', 'exception'.

## Results on open source projects
|Project|| No. of reports  | Accuracy  |
|----|  ----  | ----  |----  |
|[Sqoop](https://github.com/apache/sqoop)| Conservative | 110 |80.0% |
|| Optimistic  | 275 | 71.64% |
|[wicket](https://github.com/apache/wicket)| Conservative | 587 |89.78% |
|| Optimistic  | 1210 | 76.94% |
|[tika](https://github.com/apache/tika)| Conservative | 87 |77.01% |
|| Optimistic  | 155 | 71.61% |


## Contact
If you meet any problem when using the tool, please contact zyang@smu.edu.sg


