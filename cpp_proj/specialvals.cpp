#include "specialvals.h"

uint processorCount()
{
  uint processor_count = std::thread::hardware_concurrency();
  if (processor_count > 1){
    processor_count--;
    if (processor_count > 4)
      processor_count--;
  }
  return processor_count;
}
