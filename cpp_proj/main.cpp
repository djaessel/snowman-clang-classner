#include <iostream>

#include <QCoreApplication>
#include <QElapsedTimer>
#include <QString>

#include "classner.h"
#include "rawclass.h"
#include "structer.h"
#include "classstorer.h"
#include "classreader.h"
#include "reinterpretalter.h"
#include "functionanalyzer.h"
#include "classanalyzer.h"
#include "gotogo.h"

using namespace std;


static bool skipClassWrite = false;
static bool skipReinterpret = false;
static bool skipAnalyze = false;
static bool skipRemoveIncluded = false;
static bool skipClassAnalyze = false;
static bool skipGotoAnalyze = true; // for now since it does not fully work

static QStringList externalIncludes;


static bool argumentExists(char* arg, const char* search)
{
  QString argx(QString::fromLocal8Bit((const char*)arg, strlen(arg)));
  return (argx == QString(search) || argx.startsWith(QString(search) + QString("=")));
}

static void printElapsedTime(QElapsedTimer *elapsedTimer)
{
  ulong msecs = elapsedTimer->elapsed();
  ulong secs = msecs / 1000;
  if ((msecs % 1000) > 0) secs++;
  ulong hours = secs / 3600;
  secs = secs % 3600;
  ulong mins = secs / 60;
  secs = secs % 60;
  cout << "Time taken: " << hours << ":" << mins << ":" << secs << endl;
}

static void printExternalIncludes()
{
  cout << "External Includes: " << externalIncludes.count() << endl;
  foreach (QString includedModule, externalIncludes) {
      QStringList moduleInfo = includedModule.split('|');
      cout << " Module: " << moduleInfo[0].toStdString().c_str() << endl;
      cout << " >> " << moduleInfo[1].replace("/", QDir::separator()).toStdString().c_str() << endl;
  }
}

static void printSkipOptions()
{
  // print options
  cout << "SkipClassWrite: " << ((skipClassWrite) ? "True" : "False") << endl;
  cout << "SkipReinterpret: " << ((skipReinterpret) ? "True" : "False") << endl;
  cout << "SkipAnalyze: " << ((skipAnalyze) ? "True" : "False") << endl;
  cout << "SkipRemoveIncluded: " << ((skipRemoveIncluded) ? "True" : "False") << endl;
  cout << "SkipClassAnalyze: " << ((skipClassAnalyze) ? "True" : "False") << endl;
  cout << "SkipGotoAnalyze: " << ((skipGotoAnalyze) ? "True" : "False") << endl;
}

static void DownDir(QString dirName, QStringList* listX)
{
  QDir dir(dirName);
  const QFileInfoList list =  dir.entryInfoList();

  QFileInfo fi;
  QStringList beta;
  for (int l = 0; l < list.size(); l++)
  {
      fi = list.at(l);
      if (fi.isDir() && fi.fileName() != "." && fi.fileName() != "..")
      {
          beta.append(fi.absoluteFilePath());
      }
      else if (fi.isFile() && fi.absoluteFilePath().endsWith(".h"))
      {
          listX->append(fi.absoluteFilePath());
      }
  }

  foreach (QString s, beta) {
      DownDir(s, listX);
  }
}

static void removeIncluded(QString moduleDir, QString moduleName, QString operatingDir = "./generated_classes")
{
  bool standardDir = true;
  QString originalDir = QDir::currentPath();
  if (operatingDir != ".") {
      standardDir = false;
      operatingDir = operatingDir.replace('/', QDir::separator());
      QDir::setCurrent(operatingDir);
  }

  moduleDir = moduleDir.replace("/", QDir::separator());

  QStringList files;
  DownDir(moduleDir, &files);

  QStringList excludedDirs;
  excludedDirs.append(".git");

  QStringList fileNames;
  foreach (QString filePath, files) {
      bool foundExl = false;
      foreach (QString dirPath, excludedDirs) {
          if (filePath.contains(dirPath + QDir::separator()) || filePath.endsWith(dirPath) || filePath.startsWith(dirPath)) {
              foundExl = true;
              break;
          }
      }

      if (!foundExl) {
          if (!fileNames.contains( filePath.split(QDir::separator()).last()) ) {
              fileNames.append(filePath.split(QDir::separator()).last());
          }
      }
  }

  QString sourceFile;
  QStringList fileNamesFound;
  foreach (QString headerFile, fileNames) {
      //QDir cur(".");
      //headerFile = cur.absolutePath() + QDir::separator() + headerFile;
      cout << "FILE: " << headerFile.toStdString().c_str();
      if (QFile::exists(headerFile) && QFileInfo(headerFile).isFile()) {
          cout << " | EXISTS ";
          if (QFile::remove(headerFile)) {
              cout << "| FOUND";
              fileNamesFound.append(headerFile);
          }
      }
      cout << endl;

      sourceFile = headerFile.replace(".h", ".cpp");
      if (QFile::exists(sourceFile) && QFileInfo(sourceFile).isFile()) {
          QFile::remove(sourceFile);
      }
  }

  cout << "FOUND ONLY REAL: " << fileNamesFound.count() << endl;

  map<QString, QString> cortess;
  QString fileName, filex2;
  foreach (QString filex, files) {
      fileName = filex.split(QDir::separator()).last();

      if (fileNamesFound.contains(fileName)) {
          filex2 = filex.mid(filex.indexOf(moduleName)).replace(moduleName, moduleDir);
          cortess.insert_or_assign(fileName, filex2);
      }
  }

  QStringList allMyFiles = QDir(".").entryList(QDir::Files | QDir::NoDotAndDotDot);
  foreach (QString file, allMyFiles) {
      if (file.endsWith(".h")) {
          QFile f(file);
          if (!f.open(QFile::ReadOnly | QFile::Text))
          {
              cout << "ERROR1 file read removeIncludes: " << file.toStdString().c_str() << endl;
              continue;
          }
          QTextStream in(&f);
          QString alla = in.readAll();
          foreach (auto incl, cortess) {
              alla = alla.replace("\"" + incl.first + "\"", "\"" + incl.second + "\"");
          }
          f.close();
          QFile f2(file);
          if (!f2.open(QFile::WriteOnly | QFile::Text))
          {
              cout << "ERROR2 file write removeIncludes: " << file.toStdString().c_str() << endl;
              continue;
          }
          QTextStream out(&f2);
          out << alla;
          f2.close();
      }
  }

  // finish up and reset to original working dir
  if (!standardDir) {
      QDir::setCurrent(originalDir);
  }
}

static void setAllSkipTrue()
{
  skipClassWrite = true;
  skipReinterpret = true;
  skipAnalyze = true;
  skipRemoveIncluded = true;
  skipClassAnalyze = true;
  skipGotoAnalyze = true;
}

static void processCommandArguments(QString *filePath, int argc, char* argv[])
{
  if (argc > 0) {
      *filePath = argv[1];
      if (argc > 1) {
          for (int i = 1; i < argc; i++) {
              if (argumentExists(argv[i], "-sc"))
                  skipClassWrite = true;
              else if (argumentExists(argv[i], "-sr"))
                  skipReinterpret = true;
              else if (argumentExists(argv[i], "-sa"))
                  skipAnalyze = true;
              else if (argumentExists(argv[i], "-si"))
                  skipRemoveIncluded = true;
              else if (argumentExists(argv[i], "-sa2"))
                  skipClassAnalyze = true;
              else if (argumentExists(argv[i], "-sg"))
                  skipGotoAnalyze = true;
              else if (argumentExists(argv[i], "--skip-all"))
                  setAllSkipTrue();
              else if (argumentExists(argv[i], "--skip")){ // option with '=' at end!
                  if (!QString(argv[i]).contains("=")) {
                      cout << "Empty --skip options ignored!" << endl;
                      continue; // skip if for some reason no parameters
                  }
                  QStringList skipArgs = QString(argv[i]).split('=')[1].split(',');
                  foreach (QString skipArg, skipArgs) {
                      if (skipArg.length() == 1) {
                        switch ((char)skipArg.at(0).cell()) {
                          case 'c':
                            skipClassWrite = true;
                            break;
                          case 'r':
                            skipReinterpret = true;
                            break;
                          case 'a':
                            skipAnalyze = true;
                            break;
                          case 'i':
                            skipRemoveIncluded = true;
                            break;
                          case 'g':
                            skipGotoAnalyze = true;
                            break;
                          default:
                            cout << "Unknown skip argument: " << skipArg.at(0).cell() << endl;
                            break;
                        }
                      }
                      else if (skipArg == QString("a2"))
                        skipClassAnalyze = true;
                      else if (skipArg == QString("all"))
                        setAllSkipTrue();
                  }
              }
              else if (argumentExists(argv[i], "--includes")) {
                  //../warband_mangled_source/havok-2013
                  if (!QString(argv[i]).contains("=")) {
                      cout << "Empty --skip options ignored!" << endl;
                      continue; // skip if for some reason no parameters
                  }
                  externalIncludes = QString(argv[i]).split('=')[1].split(',');
              }
          }
      }
  }
}


int main(int argc, char *argv[])
{
  QCoreApplication a(argc, argv);

  QString filePath("");

  processCommandArguments(&filePath, argc, argv);
  printSkipOptions();
  printExternalIncludes();


  if (filePath.isEmpty()) {
      cout << "No file given!" << endl;
      return 1;
  }


  // Start program time watch
  QElapsedTimer elapsedTimer;
  elapsedTimer.start();


  cout << "Processing cpp file ..." << endl;

  ClassStorer::initValues();

  Structer structer;
  structer.readStructs(filePath);

  Classner classner;
  classner.readClassFunctions(filePath, skipClassWrite);
  vector<RawClass> classes = classner.getClasses();

  ClassStorer classStorer(structer, classes);

  if (!skipClassWrite) {
    classStorer.writeClasses();
    classStorer.updateNewCppFile(filePath/*, classes*/);
  }

  if (!skipReinterpret) {
    ReinterpretAlter reinterpret;
    reinterpret.removeReinterpret(classes);
  }

  ClassReader classReader;
  classReader.readClasses();
  map<QString, FixedClass> modifiedClasses = classReader.getClasses();

  // remove default cpp file from class check - change later with different behavior
  QStringList pathArray = filePath.split("/");
  QString fileName = pathArray.back().split(".")[0];
  modifiedClasses.erase(fileName);

  map<QString, FixedClass> bakModClasses;
  foreach (auto c, modifiedClasses) {
      bakModClasses.insert_or_assign(c.first, c.second);
  }

  if (!skipAnalyze) {
      FunctionAnalyzer funcAnalyzer;
      map<QString, FixedClass> fixedClasses = funcAnalyzer.findOriginalClass(&modifiedClasses);
      map<QString, QStringList> classIncludes = funcAnalyzer.addUsedClassImports(&fixedClasses, &classes); // FIXME: bottleneck!!!
      // fixed_classes = analyzer.removeInvalidParams(fixed_classes, classes) # FIXME: broken at the moment
      classStorer.writeClassesJust(fixedClasses, classIncludes);
  }

  if (!skipRemoveIncluded) {
      cout << "Remove included..." << endl;
      //removeIncluded(QString("../warband_mangled_source/havok-2013").replace("/", QDir::separator()), "havok-2013"); // example with Havok-2013
      foreach (QString includedModule, externalIncludes) {
          QStringList moduleInfo = includedModule.split('|');
          removeIncluded(moduleInfo[1].replace("/", QDir::separator()), moduleInfo[0]);
      }
  }

  if (!skipClassAnalyze) {
      cout << "Class Analyzing..." << endl;
      ClassAnalyzer classAnalyzer;
      classAnalyzer.findClassAttributes(&bakModClasses); // FIXME: only works when previous are done and skipped second run
      // TODO: later retrieve actual attributes maybe and then store in actual class files etc.
  }

  if (!skipGotoAnalyze) {
      GoToGo gotogo;
      gotogo.processClasses(&modifiedClasses);

      QStringList files = QDir(".").entryList(QDir::Files | QDir::NoDotAndDotDot);
      foreach (QString file, files) {
          if (file.contains("_") && file.endsWith(".cpp")) {
              QFile fx(file);
              fx.copy(QString("./endl/class_info/" + file).replace("/", QDir::separator()));
              fx.remove();
          }
      }
  }


  // Stop program time watch
  printElapsedTime(&elapsedTimer);
  elapsedTimer.invalidate();

  return 0;
}
