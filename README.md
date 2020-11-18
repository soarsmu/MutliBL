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
The sequence of each column in .xlsx files should be:
1. ISSUENO
2. DISCRIPT
3. CREATER
4. SDEPT3SUBMIT
5. BVERSION
6. DETAILDESCRIPTION
7. FILE_PATH
8. CREATE_TIME
9. FEATURE
10. MODULE

[**Please Notice**] 1st must be ISSUENO (bug id), 2nd must be DISCRIPT (summary), 6th must be DETAILDESCRIPTION (detail description), 7th must be FILE_PATH (ground truth), and 8th must be CREATE_TIME.

## Environment Configuration
Having conda installed on your machine, please execute `bash env_config.sh` to create a virtual environment and install necessary dependencies.

## Running Configuration
Make sure that you are in the root path of this repo. There should be a `./result` folder in the repo (if not, please create one), and the generated file will be stored in this folder.

### Configuring bug information

You need to specify bug information in `config.ini` file, including:
* repo_name: we set it as "HUAWEI"
* path_to_bug_report_sheet: path to the .xlsx that stores bug report information
* path_to_original_codebase: path to the codebase

### Configuring running mode
The tool runs in two modes:
* Optimistic filtering mode: generating buggy file recommendations for all bug report received;
* Conservative filtering mode: generating fewer recommendations, but recommendations are more trustworthy.

You can specify the mode in `config.ini`. You can also choose "all" to see the results of the two modes at the same time.

### Configuring translation function
You can tell the tool whether you want to translate the bug reports and comments in the codebase by specifying `is_translation_required` in `config.ini`.

[**PLEASE Notice**]: The translation function is **NOT** implemented, since it can be risky to use translation service outside HUAWEI. Currently, the tool can run but the translator only returns the original text. You may change `translator(text)` function (Line 125, in `translator.py`) to enable translating Chinese to English functionality.

## Running the tool
After you configuring environment and specifying necessary information, you can run the tool with `python multibl.py`
There are five steps:
* Step 0: converting .xlsx file into .xml file
* Step 1: Executing translation (if required)
* Step 2: Preprocessing bug reports, drops invalid ones
* Step 3: Localizing buggy files
* Step 4: Generating summary results



## Results on open source projects
|Project|| No. of reports  | Accuracy  |
|----|  ----  | ----  |----  |
|[Sqoop](https://github.com/apache/sqoop)| Conservative | 110 |80.0% |
|| Optimistic  | 275 | 71.64% |
|[wicket](https://github.com/apache/wicket)| Conservative | 587 |89.78% |
|| Optimistic  | 1210 | 76.94% |
|[tika](https://github.com/apache/tika)| Conservative | 87 |77.01% |
|| Optimistic  | 155 | 71.61% |

Here an 'accurate' recommendation means that the tool ranks a related bug file in top 10. 

To replicate the above results, you can find bug reports data for the three repositories in `/bugzbook_data/sheet`. You also need to clone these repos and configure `path_to_original_codebase` in `config.ini` file. For example, you can `mkdir codebase_data` under `/bugzbook_data`, and clone repos by:
* git clone https://github.com/apache/sqoop
* git clone https://github.com/apache/wicket
* git clone https://github.com/apache/tika

## Contact
If you have any questions or meet any problem when using the tool, feel free to contact zyang@smu.edu.sg


