import argparse
# from get_files_hash_values import get_files_hash_values
# import find_new_assets
import csv
import hashlib
import os
import re
import time

existing_manifest_csv_path = 'test_files/2_1_2018.csv'
new_files_dir = '../../../../../ahpn/misha_test/ahpn_2019/2/2'
# new_calculated_hashes = 'test_files/ahpn-misha_test-2-2-hash_values.csv'

new_manifest_list = [
  {'file': '17427196.tif', 'path': '2/1/17427196.tif', 'hash': 'ea756afc8bb793d9dda6b6ef8086c62f2065a295c59bc95680eed5d53d6b4c68', 'file_size': 50545},
  {'file': '17427197.tif', 'path': '2/1/17427197.tif', 'hash': 'b3f35eda4bbbf5ed40adbba4104e584969c16332df846a2f289dcad6f5380898', 'file_size': 131168},
  {'file': '17427198.tif', 'path': '2/1/17427198.tif', 'hash': '3e4f7e27c5742dbbc55bf019a827409f9bbb2cec556ddfc923e4d293d480e88c', 'file_size': 154177},
  {'file': '17427199.tif', 'path': '2/1/17427199.tif', 'hash': '24b30fc3fcdadf9e0bb36e6be3e2084ab35e7ec140110395d4c88b575bed3329', 'file_size': 68948},
  {'file': '17427200.tif', 'path': '2/1/17427200.tif', 'hash': '4bdf0fe0cc6a870d793768a6c5d624c927cb07e97bb9cf231f42085a67914e93', 'file_size': 156391},
  {'file': '10014110.tif', 'path': '2/1/10014110.tif', 'hash': '80fb9ac2daf2cf5c7ee59b6fd5d423641eab110da771a9c3c39722a316d62abe', 'file_size': 183623},
  {'file': '17427201.tif', 'path': '2/1/17427201.tif', 'hash': '56e716a99e86444d88545a2ca3ee7fbff4d515727d5aba0f75a66fb89b592286', 'file_size': 99158},
  {'file': 'bogus.tif', 'path': '2/1/bogus.tif', 'hash': 'fakefakefakefakefakefakefakefakefakefake9b592286', 'file_size': 99158},
  {'file': '17427863.tif', 'path': '2/1/17427863.tif', 'hash': 'ba918760d29b63a8cdb37fde90c9b6dae91393ea525a3ef06beb8522b73d10fc', 'file_size': 17172},
  {'file': '17470374.tif', 'path': '2/1/17470374.tif', 'hash': 'd791fb8a28f886dae9781b689b1c66ba064b7a81db225d896c0cd4a718a3ee15', 'file_size': 115478},
  {'file': '17470375.tif', 'path': '2/1/17470375.tif', 'hash': '79aa184189b9ac2b5401a32f9522e6bc6cf766d04e649467e0e8892f79087b31', 'file_size': 124963},
  {'file': '17470376.tif', 'path': '2/1/17470376.tif', 'hash': '991643e3c890962c2dd7b7ab52fb7e2ba24ae4158e431c13035998ad437400dd', 'file_size': 1246816},
  {'file': '11193087.tif', 'path': '2/1/11193087.tif', 'hash': 'ea411a0f9529b173d0ecd719782f7a93d323d8bc061c6cb84326c22ca5d7273a', 'file_size': 34120},
  {'file': '11194577.tif', 'path': '2/1/11194577.tif', 'hash': '5a26bcda9b9029b2e9080feeab708ddbf90b752fe61ec1079b92769cca2bef98', 'file_size': 32518}
]

# Takes file path to existing manifest csv
# Converts Windows file paths to Unix style
# Returns list of dictionaries with a hash and file path for each item
def unixify_existing_manifest(existing_manifest_path):
  print('Preparing existing manifest for comparison...')
  with open(existing_manifest_path, 'r') as file:
    csv_reader = csv.reader(file, delimiter=',', quotechar='"')
    manifest_list = []

    for row in csv_reader:
      row_dict = {}

      unixified_file_name = re.sub(r'\\', r'/', row[1])
      row_dict['hash'] = row[0]
      row_dict['path'] = unixified_file_name

      manifest_list.append(row_dict)

    return manifest_list

# This is a rip-off of functions from calculate_hash_values repo.
# Modifications: Returns list of lists, not csv.
# Calculates sha-256 (not md5) to conform to existing manifests for AHPN.
def hash_file(file_path):
    hash = hashlib.sha256()
    buffer_size = 65536
    hash_value = ''

    # Print dialog for each file while calculating hash
    print('Calculating hash for:', file_path)

    with open(file_path, 'rb') as file:
        while True:
            data = file.read(buffer_size)
            if not data:
                break
            hash.update(data)

    file_size = os.path.getsize(file_path)

    hash_value = [hash.hexdigest(), file_size]

    return hash_value

# Takes file path to new files directory (2019 disk)
# Run get file hash values
# Returns list of dictionaries with file name, its absolute path, sha-256 hash value, and file size
def calculate_new_manifest(new_files_root_dir):
  print('Calculating new manifest for', new_files_root_dir)
  new_manifest_list = []

  for root, dirs, files in os.walk(new_files_root_dir):
    for file in files:
      hash_path_dict = {}

      abs_path = os.path.abspath(os.path.join(root, file))
      hash_value = hash_file(abs_path)

      hash_path_dict['file'] = file
      hash_path_dict['path'] = abs_path
      hash_path_dict['hash'] = hash_value[0]
      hash_path_dict['file_size'] = hash_value[1]

      new_manifest_list.append(hash_path_dict)

  return new_manifest_list

# Take 2
# Find matches, then subtract list of matches from new files list
def find_matches(list_1, list_2):
  matches = []

  # Loop through rows in first file to begin comparison
  for row in list_1:
    hash_1 = row['hash']
    path_1 = row['path']

    # Compare to each row in the csv_2 list
    for row in list_2:
      hash_2 = row['hash']
      path_2 = row['path']
      file_name_2 = row['file']

      # If match found, create match list and append match to matches list
      if hash_1 == hash_2:
          match = [hash_1, path_1, path_2, file_name_2]
          
          matches.append(match)

  return matches

def write_list_to_csv(copy_list):
  timestamp = time.strftime("%Y%m%d-%H%M%S")
  output_file_name = 'aphn-copy-list-' + timestamp + '.csv'

  # If no matches found, do not write csv, return message
  if len(copy_list) <= 0:
    print('No unmatched files to copy.')

  # Else, write each match to a csv row
  else:
    with open(output_file_name, 'a', newline='', encoding='utf-8') as output_csv:
      writer = csv.writer(output_csv, quotechar='"', delimiter=',')
        
      for row in copy_list:
        out_row = [row['path'], row['hash']]
        writer.writerow(out_row)

# Change existing manifest file paths to unix format
existing_manifest_list = unixify_existing_manifest(existing_manifest_csv_path)

# Calculate hash values for new files
# new_manifest_list = calculate_new_manifest(new_files_dir)
# print('new manifest:', new_manifest_list[0].get('hash'))

# copy_list = find_new_assets.find_new_assets(existing_manifest_list, new_manifest_list)
copy_list = find_matches(existing_manifest_list, new_manifest_list)
print('copy list:', copy_list)
print('new manifest list length:', len(new_manifest_list))
print('copy list length:', len(copy_list))

# write_list_to_csv(copy_list)