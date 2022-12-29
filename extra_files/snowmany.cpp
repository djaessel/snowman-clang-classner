int64_t zero_stack_offset()
{
    int64_t stack_offset = 0;
    asm("movq %%rsp, %0" : "=r" (stack_offset));
    return stack_offset;
}
