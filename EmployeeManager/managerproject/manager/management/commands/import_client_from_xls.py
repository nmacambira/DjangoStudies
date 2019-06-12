# manager/management/commands/import_client_from_xls

import xlrd
from django.core.management.base import BaseCommand, CommandError
from django.utils.encoding import smart_str
from manager.models import Client

SILENT, NORMAL, VERBOSE, VERY_VERBOSE = 0, 1, 2, 3


class Command(BaseCommand):
       help = "Imports clients from a local XLS file. " \
              "Expects name, email."

       def add_arguments(self, parser):
           parser.add_argument('file_path')

       def handle(self, *args, **options):
           print("Reading xls...")
           file_path = options['file_path']
           wb = xlrd.open_workbook(file_path)
           print("The number of worksheets is {0}".format(wb.nsheets))
           print("Worksheet name(s): {0}".format(wb.sheet_names()))

           verbosity = int(options.get("verbosity", NORMAL))
           if verbosity >= NORMAL:
               print("=== XLS file imported ===")

           first_sheet = wb.sheet_by_index(0)  # get a single sheet
           # print("{0} {1} {2}".format(first_sheet.name, first_sheet.nrows, first_sheet.ncols))

           for sh in wb.sheets():
               # let's skip the first sheet
               if sh != first_sheet:
                   print("Sheet name: {0}; number of rows: {1}; numbers of columns: {2};".format(sh.name, sh.nrows,
                                                                                                 sh.ncols))
                   for rownum in range(sh.nrows):
                       # let's skip the column captions and blank rows
                       if rownum > 2:
                           (name, email, telephone, address) = sh.row_values(rownum)
                           client, created = Client.objects.get_or_create(
                               name=name,
                               email=email,
                           )
                           if verbosity >= NORMAL:
                               print(" - %s" % smart_str(client.name))


# pip install xlrd

# command to run from terminal: python manage.py import_client_from_xls /Users/<Username>/Documents/<MyApp>/clients.xls

