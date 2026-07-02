In this folder, we have the mcbuild source files.

Basically they will be copied into one single build folder when building.
This process is controlled by beet.

Some of the folder or files won't be copied due to module management or switches between different implements.

In instruction implements, there may be comments like this:
```python
# The comment below is to help the project locate the instruction definitions.
# Do not remove.

# #BEGIN INST DEF

...

# #END INST DEF

# The comment above is to help the project locate the instruction definitions.
# Do not remove.
```
This used in the inline expension.
Check [main README](../../README.md#text-storage).

To keep the simpilicity, the area inside it **should not** use
braces with nesting depth larger than 1.