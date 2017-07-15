from requests import Session
import mmap
from os import path
import os
from progress.bar import Bar
from concurrent import futures
import sys


API_ENDPOINT = 'https://api.evasrv.com/email_verification/'
API_TOKEN = 'YOUR TOKEN GOES HERE'

session = Session()

def load_url(email):
    """Run API call and returns response object.

    :param email:
    :return:
    """
    headers = {
        'cache-control': "no-cache",
        'content-type': "application/x-www-form-urlencoded"
    }

    data = {
        'email': email,
        'user_API_token': API_TOKEN
    }

    return session.post(url=API_ENDPOINT, data=data, headers=headers)


def get_thread_count():
    count = input('How many threads would you like to run? [5]: ')

    if not count:
        count = 5

    try:
        int(count)
    except Exception as e:
        print('Invalid number.')
        sys.exit(2)

    print('Using {} threads.'.format(count))

    return int(count)


def get_file_names():
    """Prompt user for file name that contains emails and returns that name as well as the name of the file
    where results should be written.

    Example: ('emails.txt','emails-valid.txt')

    It also checks to ensure results file name doesn't already exist.

    :return: [email_file_name, results_name]
    """

    filename = input("What file are email addresses in? (Example: emails.txt): ")

    filename_noext, ext = path.splitext(filename)
    export_filename = '{}-valid{}'.format(filename_noext, ext)

    if path.exists(export_filename):
        print("The results would be written here but this file exists: {}".format(export_filename))
        delete = input("Delete {} first? [y|N] ".format(export_filename))
        if delete == 'y':
            os.remove(export_filename)
        else:
            print('The results file cannot be created because it already exists: "{}"'.format(export_filename))
            sys.exit(3)

    return filename, export_filename


def get_email_file(filename):
    """Return file pointer where email addresses are stored.

    :param filename: Filename of emails file.
    :return: File pointer.
    """

    try:
        emails_file = open(filename, 'r+', encoding='utf8')
    except FileNotFoundError:
        raise Exception('Could not find file "{}".'.format(filename))
    except IOError:
        raise Exception('Could not read file "{}".'.format(filename))

    return emails_file


def get_filemap(fp):
    """Get file map object and close file.

    :param fp: File object.
    :return:
    """

    fmap = mmap.mmap(fp.fileno(), 0)
    fp.close()
    return fmap


def validator(file_map, result_filename, thread_count):
    headers = {
        'cache-control': "no-cache",
        'content-type': "application/x-www-form-urlencoded"
    }

    result_file = open(result_filename, 'w', encoding='utf8')

    with futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
        future_to_url = {}

        valid_emails = []

        while True:
            line = file_map.readline()

            if line:
                email = line.split(b';')[0]
            else:
                break

            future_to_url[executor.submit(load_url, email)] = line

        bar = Bar('Valid/Invalid: 0/0', max=len(future_to_url.keys()), suffix='%(percent)d%%')

        resp_err = 0
        resp_ok = 0
        valid = 0
        invalid = 0
        for future in futures.as_completed(future_to_url):

            line = future_to_url[future]

            try:
                response = future.result()
                if response.ok:
                    json = response.json()
                    if json['status'] == 'Valid':
                        valid += 1
                        valid_emails.append('{}\n'.format(line.decode("utf-8").replace('\n',''))) # use our own new line
                    else:
                        invalid += 1
                    bar.message = 'Valid/Invalid: {}/{}'.format(valid, invalid)
                else:
                    print(b"Error in request for email: " + line)
                    response.raise_for_status()
            except Exception as exc:
                resp_err = resp_err + 1
            else:
                resp_ok = resp_ok + 1

            bar.next()

        print('\nSuccessful runs: {}'.format(resp_ok))
        print('Failed runs: {}'.format(resp_err))

        result_file.writelines(valid_emails)

    result_file.close()


def main():
    thread_count = get_thread_count()
    emails_filename, result_filename = get_file_names()
    file = get_email_file(emails_filename)

    validator(get_filemap(file), result_filename, thread_count)

if __name__ == '__main__':
    # pass
    main()
