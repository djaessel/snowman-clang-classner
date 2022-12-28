#include <iostream>

#include <QCoreApplication>
#include <QString>

#include "classner.h"
#include "rawclass.h"
#include "structer.h"
#include "classstorer.h"
#include "classreader.h"
#include "reinterpretalter.h"

using namespace std;

static bool skipClassWrite = false;
static bool skipReinterpret = false;
static bool skipAnalyze = false;
static bool skipRemoveIncluded = false;
static bool skipClassAnalyze = false;


static bool argumentExists(char* arg, const char* search)
{
  return QString::fromLocal8Bit((const char*)arg, strlen(arg)) == QString(search);
}

int main(int argc, char *argv[])
{
//  QCoreApplication a(argc, argv);

  QString filePath = "";

  if (argc > 0) {
      filePath = argv[1];
      if (argc > 1) {
          for (int i = 1; i < argc; i++) {
              if (argumentExists(argv[i], "-sc"))
                  skipClassWrite = true;
              if (argumentExists(argv[i], "-sr"))
                  skipReinterpret = true;
              if (argumentExists(argv[i], "-sa"))
                  skipAnalyze = true;
              if (argumentExists(argv[i], "-si"))
                  skipRemoveIncluded = true;
              if (argumentExists(argv[i], "-sa2"))
                  skipClassAnalyze = true;
              if (argumentExists(argv[i], "--skip-all")){
                  skipClassWrite = true;
                  skipReinterpret = true;
                  skipAnalyze = true;
                  skipRemoveIncluded = true;
                  skipClassAnalyze = true;
              }
          }
      }
  }

  if (filePath.isEmpty()) {
      cout << "No file given!" << endl;
      return 1;
  }

  //stopwatch = Stopwatch()
  //stopwatch.start()

  cout << "Processing cpp file ..." << endl;

  ClassStorer::initValues();

  Structer structer;
  structer.readStructs(filePath);

  Classner classner;
  classner.readClassFunctions(filePath, skipClassWrite);
  vector<RawClass> classes = classner.getClasses();

  ClassStorer classStorer(structer, classes);

  if (skipClassWrite) {
    classStorer.writeClasses();
    classStorer.updateNewCppFile(filePath, classes);
  }

  if (skipReinterpret) {
    ReinterpretAlter reinterpret;
    reinterpret.removeReinterpret(classes);
  }

  ClassReader classReader;
  classReader.readClasses();
  auto modified_classes = classReader.getClasses();

//  return a.exec();
  return 0;
}
