# Advanced Clean Coding Review Rules for Github Copilot. Review aspects: SOLID Principles, Error Handling, Formatting, Unit tests / Testing, Classes, Objects and Data Structures

- **context setting**: Write focused review comments for the selected code based on the review instructions(e.g. CCA1, CCA2 ..etc) provided below.

#========================== SOLID Principles ==============================#
- **CCA1**: **Check Single Responsibility Principle (SRP)**. Verify that each class has only one reason to change, ensuring a single well-defined responsibility.
- **CCA2**: **Check Open/Closed Principle (OCP)**. Confirm that classes are open for extension but closed for modification (e.g., using interfaces or abstract classes).
- **CCA3**: **Check Liskov Substitution Principle (LSP)**. Subclasses should be fully substitutable for their base classes without affecting correctness.
- **CCA4**: **Check Interface Segregation Principle (ISP)**. Avoid forcing classes to implement interfaces they do not use. Split large interfaces into smaller, more specific ones.
- **CCA5**: **Check Dependency Inversion Principle (DIP)**. Ensure that high-level modules do not depend on low-level modules; both should depend on abstractions.

#========================== Error Handling ================================#
- **CCA6**: **Check appropriate exception usage**. Use exceptions for truly exceptional cases, not regular control flow.
- **CCA7**: Ensure potential errors are handled gracefully. Handle each plausible error condition rather than ignoring it.
- **CCA8**: **Avoid swallowing exceptions**. Always log or act upon caught exceptions; do not silently discard them.
- **CCA9**: **Use logging and assertions**. When errors occur, ensure they’re properly logged; assertions may be used to validate assumptions.
- **CCA10**: **Review try/catch usage**. Adding too many try/catch blocks can clutter error handling and make analysis difficult.
- **CCA11**: **Check corner-case exception blocks**. They are valid if truly needed; otherwise, avoid them.
- **CCA12**: **Scrutinize new try/catch blocks**. Only add them if absolutely required after careful review.

#========================== Formatting ====================================#
- **CCA13**: Check indentation consistency (2 or 4 spaces). Ensure uniform indentation across the codebase.
- **CCA14**: Use line breaks and whitespace to improve readability.
- **CCA15**: Restrict line length to 80–120 characters. This prevents horizontal scrolling and improves clarity.
- **CCA16**: Vertically group caller and callee. The calling function should be placed above the function it calls.
- **CCA17**: Apply vertical formatting. High-level concepts go at the top; detailed implementations go toward the bottom.
- **CCA18**: Maintain vertical openness between similar concepts. Keep related items together with minimal blank lines.
- **CCA19**: Keep variables close to usage. Declare them in the narrowest possible scope.
- **CCA20**: Group conceptually related functions. E.g., overloaded methods should be placed adjacent to each other.
- **CCA21**: Limit horizontal length. Avoid lines longer than 120 characters.
- **CCA22**: Use horizontal whitespace wisely. Keep closely related tokens together (`var++`, `*pointer`) and separate unrelated ones with spaces.
- **CCA23**: Avoid horizontal alignment. Do not align variables or parameters into columns.
- **CCA24**: Keep indentation uniform for control structures. Always put the brace on a new line instead of having in the same line as function name.
- **CCA25**: Use dummy scopes carefully. If a loop body is empty, place the semicolon on its own line with correct indentation.

#========================== Unit tests / Testing ===========================#
- **CCA26**: Write unit tests for all critical functions to validate correctness and catch regressions.
- **CCA27**: **Follow TDD (Test-Driven Development)** when possible. Write tests before implementing features.
- **CCA28**: Use meaningful test names to clarify what scenario is being tested.
- **CCA29**: Do not deliver production code without tests. All shipped code should be covered by unit tests.
- **CCA30**: For bug fixes first add a failing test that reproduces the bug, then fix the code.

## Clean Test
- **CCA31**: Leverage utility methods for setup to keep tests short and readable.
- **CCA32**: Apply standard naming conventions in tests as in production code.
- **CCA33**: Limit one `assert` per test unless verifying multiple fields of the same object.
- **CCA34**: Use `ON_CALL with Mock objects to specify return values or behavior.

## F.I.R.S.T
- **CCA35**: **Fast** — Tests should run quickly. Avoid slow constructs like `EXPECT_DEATH` unless absolutely necessary.
- **CCA36**: **Independent** — Tests should not depend on each other’s side effects.
- **CCA37**: **Repeatable** — Tests should pass in any environment (production, QA, CI).
- **CCA38**: **Self-validating** — Tests should produce clear pass/fail outcomes without manual log inspection.
- **CCA39**: **Timely** — Tests should be written as features are developed, helping catch issues early.

#========================== Classes =======================================#

## Class organization
- **CCA40**: **Follow a logical class layout**: constructor(s), member functions, then member variables.
- **CCA41**: Keep member variables private along with utility methods not needed externally.
- **CCA42**: Ensure classes are small. Each class should handle a single responsibility.
- **CCA43**: Maintain cohesion. Each method should operate on at least one member variable; otherwise, consider moving it.

#========================== Objects and Data Structures ===================#

## Data Abstraction
- **CCA44**: Do not expose internal members. Public fields break encapsulation.
- **CCA45**: Avoid trivial setters for every member. Use logical methods that operate on internal data instead.
- **CCA46**: Ensure meaningful data operations. Return computed or processed results instead of raw internal data.

## The Law of Demeter
- **CCA47**: **Check function call chaining**. A method `f` in class `C` should only call methods of:
  1) `C` itself
  2) Objects created by `f`
  3) Objects passed as arguments
  4) Objects held in `C`’s member variables
- Remember that The Law of Demeter applies to objects, not bare data structures.
- **CCA48**: **Avoid train wrecks** (`object1.f1().f2().f3()`). Instead, have `object1` provide a single method that internally delegates as needed
- **CCA49**: **Data Transfer Objects** Check Data Transfer Objects (DTOs) to ensure they contain only data with no business logic. It’s acceptable for DTOs to have public members or simple getter/setter methods (if members are private), provided they remain strictly for data transfer purposes.
