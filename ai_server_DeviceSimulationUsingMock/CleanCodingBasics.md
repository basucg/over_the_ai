# Basic Clean Coding Review Rules for Github Copilot. Review aspects: General Principles, Naming Conventions, Functions, Comments, Code Structure

- **context setting**: Write focused review comments for the selected code based on the review instructions(e.g. CCB1, CCB2 ..etc) provided below.

#======================== General Principles ============================#
- **CCB1**: **Check if the code is clear and readable**. The code should be self-explanatory and easy to understand without excessive comments.
- **CCB2**: **Check for magic numbers or strings**. Constants or enums should be used instead.
- **CCB3**: **Apply KISS (Keep It Simple, Stupid)**. Code should remain simple and straightforward, avoiding unnecessary complexity.

#======================== Naming Conventions ============================#
- **CCB4**: Check camelCase usage for variables and functions.
- **CCB5**: Check PascalCase usage for classes and constructors.
- **CCB6**: Confirm that names are meaningful, descriptive and describe the purpose or intent of the variable/function.
- **CCB7**: Check if consistent naming conventions are followed.
- **CCB8**: Avoid unclear abbreviations unless they are widely understood (e.g., `URL`, `ID`).
- **CCB9**: Use pronounceable names for better clarity.
- **CCB10**: **Add meaningful context**. If multiple related variables can form a structure, wrap them in a class/structure.
- **CCB11**: **Avoid gratuitous context**. Do not prefix every class name for a module with the same prefix.
- **CCB12**: Avoid disinformation by using short, standard abbreviations only. For non-standard abbreviations, use full names.
- **CCB13**: **Make meaningful distinctions** For similar variable/class types, choose names that clearly reveal differences (e.g., `lhs/rhs` instead of `input1/input2`).
- **CCB14**: Use “m_” prefix for member variables.
- **CCB15**: Prefix interfaces and implementations with “I”.
- **CCB16**: Use noun-based class names that represent real-life entities.

## Use Intention-Revealing Names
- **CCB17**: Check if names indicate the “why” and “how.” Class, function, or variable names should clearly convey their purpose.
- **CCB18**: Ensure proper naming in tests. Test names can follow the pattern: `Intention_input_expected`.

## Use Searchable Names
- **CCB19**: Ensure variable/object names are easily searchable. Names should yield minimal but relevant search results.
- **CCB20**: Avoid generic words like ‘error’ or ‘status’ unless context is clearly stated or wrapped in a descriptive class/structure.
- **CCB21**: If variables are part of a class/structure, a plain name may suffice if the class context is clear.

## Avoid Encodings
- **CCB22**: Do not use bit-length or type encodings in names (e.g., `u8Status`).
- **CCB23**: **Avoid appending types** Use names like `Status` instead of `u8Status`; if multiple formats exist, clarify (e.g., `StatusAsString`, `StatusAsInt`).

## Method Names
- **CCB24**: Check if method names use verbs or verb phrases.
- **CCB25**: Avoid puns or ambiguous terms.
- **CCB26**: Ensure one word maps to one concept. Do not reuse the same word for different concepts.
- **CCB27**: **Use solution domain names**. Use common CS, algorithm, or pattern names (e.g., “Factory,” “Observer,” etc.). E.g.: `ShowRouteCommand` (the word “Command” indicates the pattern).

#============================= Functions =================================#
- **CCB28**: **Limit function arguments**. Ideally, a function should have no more than 3 arguments.
- **CCB29**: **Use default arguments** for optional parameters when possible.
- **CCB30**: **Avoid side effects**. Functions should not modify global state or arguments unexpectedly.
- **CCB31**: **Return early**. Use guard clauses for edge cases at the start of the function.
- **CCB32**: **Adhere to DRY(Don’t Repeat Yourself)**. If logic repeats in multiple places, refactor it into a single function.
- **CCB33**: **Keep if/else blocks concise**. If multiple lines are needed, move them to a separate function.

## Small
- **CCB34**: Function length should serve one purpose. Ensure it does the work of “one thing.”
- **CCB35**: Avoid strict line limits, focus on singular responsibility instead.

- **CCB36**: Maintain one level of abstraction per function. Use the step-down rule for clarity. Organize functions top-down to read like a narrative.

## Switch Statements
- **CCB37**: **Avoid large switch blocks**. Many cases can lead to sprawling code.
- **CCB38**: **Use an abstract factory**. Each case can instantiate the required class, limiting switch usage to one factory class.
- **CCB39**: **Exception**: If performing simple data type conversions, direct switch usage is acceptable.

## Use descriptive names
- **CCB40**: Check if function names reveal their actions
- **CCB41**: Longer names are acceptable if they clearly describe the function’s job.

## Function arguments
- **CCB42**: 0 arguments (niladic) is ideal followed by 1 (monadic), then 2 (dyadic).
- **CCB43**: Avoid triadic (3 arguments) where possible.
- **CCB44**: For more than 3 arguments ensure a valid reason if the function still does only one job.
- **CCB45**: Group arguments in a class/structure if they become too numerous.
- **CCB46**: Avoid output arguments wherever possible.

## Command query separation
- **CCB47**: Check if functions do either an action or return data, but not both.
- **CCB48**: Setters should not return values and getters should not alter state.

#============================== Comments ===================================#
- **CCB49**: Ensure comments explain ‘why not merely ‘what.’
- **CCB50**: Verify comments are updated alongside code changes.
- **CCB51**: Avoid redundant comments that restate obvious behavior.
- **CCB52**: Remove commented-out code from source files.
- **CCB53**: Avoid non-local design comments that belong in documentation rather than inline.
- **CCB54**: Limit comment detail Include only necessary information.

## Explain yourself in code
- **CCB55**: Code clarity should reduce the need for comments
- **CCB56**: If code is expressive, comments become optional.

## Good Comments
- **CCB57**: **Legal comments**: e.g., copyright statements.
- **CCB58**: **Warnings of consequences**: If misuse leads to significant issues, state it.
- **CCB59**: **TODO statements**: Indicate incomplete tasks or planned features.

## Bad Comments
- **CCB60**: **Mumbling**: A placeholder comment in an empty `else` is unhelpful.
- **CCB61**: **Redundant comments**: Header comments that repeat what the code does are unnecessary.
- **CCB62**: **Misleading comments**: Outdated comments that conflict with current logic must be removed or updated.
- **CCB63**: **Journal comments**: Commit history belongs in SCM, not in the source file.
- **CCB64**: **Noise comments**: Re-stating function names or obvious details is redundant.
- **CCB65**: **Position markers**: Avoid `/////` lines or similar markers.

## Closing brace comments
- **CCB66**: Avoid adding comments at the end of braces
- **CCB67**: If many nested loops/conditions exist consider refactoring into smaller functions.

#========================== Code Structure ================================#
- **CCB68**: **Organize code logically**: group related items (e.g., properties first, then methods).
- **CCB69**: **Use modules/namespaces**: Split large files into manageable modules.
- **CCB70**: **Apply SRP (Single Responsibility Principle)**: Each module/class should have only one reason to change.
