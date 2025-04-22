# Control Flow and Variables

This document explains how to use control flow and variables in the workflow builder.

## Table of Contents

- [Overview](#overview)
- [Variables](#variables)
  - [Set Variable Node](#set-variable-node)
  - [Get Variable Node](#get-variable-node)
- [Control Flow](#control-flow)
  - [For Loop Node](#for-loop-node)
  - [While Loop Node](#while-loop-node)
  - [Compare Node](#compare-node)
  - [Conditional Node](#conditional-node)
- [Examples](#examples)
  - [Counter Example](#counter-example)
  - [Processing List Example](#processing-list-example)
- [Best Practices](#best-practices)

## Overview

The workflow builder provides a flexible system for handling control flow and variables. You can use explicit variable nodes to store and retrieve values, and control flow nodes to create loops and conditionals.

## Variables

Variables allow you to store and retrieve values in your workflow. They are useful for:

- Storing intermediate results
- Passing data between nodes
- Keeping track of state

### Set Variable Node

The Set Variable node allows you to store a value with a name.

**Inputs:**
- `value`: The value to store
- `trigger`: Execution trigger (optional)

**Outputs:**
- `value`: The stored value
- `completed`: Triggered when the variable is set

**Configuration:**
- `variable_name`: The name of the variable

**Example:**
```
[Text Input] → [Set Variable: "message"] → [Next Node]
```

### Get Variable Node

The Get Variable node allows you to retrieve a stored value by name.

**Inputs:**
- `trigger`: Execution trigger (optional)

**Outputs:**
- `value`: The variable value
- `exists`: Whether the variable exists

**Configuration:**
- `variable_name`: The name of the variable
- `default_value`: The default value to return if the variable doesn't exist

**Example:**
```
[Get Variable: "message"] → [Text Output]
```

## Control Flow

Control flow nodes allow you to create loops, conditionals, and other flow control structures in your workflow.

### For Loop Node

The For Loop node iterates over a list of items and executes connected nodes for each item.

**Inputs:**
- `items`: The list of items to iterate over
- `trigger`: Execution trigger

**Outputs:**
- `completed`: Triggered when the loop completes
- `current_item`: The current item in the iteration
- `index`: The current iteration index
- `results`: Collected results from all iterations

**Configuration:**
- `item_variable`: The name of the variable to store the current item
- `index_variable`: The name of the variable to store the current index
- `collect_results`: Whether to collect results from the loop body
- `result_variable`: The name of the variable to store the collected results

**Example:**
```
[Array Input] → [For Loop] → [Completed] → [Next Node]
                    ↓
                [Current Item] → [Process Item] → [Output]
```

### While Loop Node

The While Loop node executes connected nodes while a condition is true.

**Inputs:**
- `condition`: The loop condition
- `trigger`: Execution trigger

**Outputs:**
- `completed`: Triggered when the loop completes
- `iteration`: Triggered for each iteration
- `iteration_count`: The number of iterations completed
- `results`: Collected results from all iterations

**Configuration:**
- `max_iterations`: The maximum number of iterations
- `iteration_variable`: The name of the variable to store the current iteration
- `collect_results`: Whether to collect results from the loop body
- `result_variable`: The name of the variable to store the collected results

**Example:**
```
[Boolean Input] → [While Loop] → [Completed] → [Next Node]
                      ↓
                  [Iteration] → [Process] → [Update Condition]
```

### Compare Node

The Compare node compares two values and outputs a boolean result.

**Inputs:**
- `value_a`: The first value to compare
- `value_b`: The second value to compare
- `trigger`: Execution trigger (optional)

**Outputs:**
- `result`: The comparison result
- `true_output`: Triggered if the comparison is true
- `false_output`: Triggered if the comparison is false

**Configuration:**
- `operator`: The comparison operator (eq, ne, gt, ge, lt, le, contains, startswith, endswith)
- `result_variable`: The name of the variable to store the result

**Example:**
```
[Number Input] → [Compare: "<"] → [Result] → [Conditional]
                     ↑
              [Number Input]
```

### Conditional Node

The Conditional node executes different branches based on a condition.

**Inputs:**
- `condition`: The condition to evaluate
- `trigger`: Execution trigger
- `value`: The value to pass to the selected branch (optional)

**Outputs:**
- `true_output`: Triggered if the condition is true
- `false_output`: Triggered if the condition is false
- `result`: The value from the selected branch

**Configuration:**
- `condition_variable`: The name of the variable to store the condition
- `result_variable`: The name of the variable to store the result

**Example:**
```
[Boolean Input] → [Conditional] → [True] → [Process True]
                       ↓
                   [False] → [Process False]
```

## Examples

### Counter Example

This example demonstrates a simple counter using a while loop:

1. Set a variable `counter` to 0
2. While `counter < 10`:
   a. Increment `counter` by 1
   b. Output the current value of `counter`
3. Output "Done" when the loop completes

```
[Set Variable: "counter" = 0] → [While Loop] → [Completed] → [Text Output: "Done"]
                                    ↓
                                [Iteration] → [Get Variable: "counter"] → [Math: "+1"] → [Set Variable: "counter"]
                                                                            ↓
                                                                        [Text Output]
```

### Processing List Example

This example demonstrates processing a list of items using a for loop:

1. Create a list of items
2. For each item in the list:
   a. Convert the item to uppercase
   b. Add the uppercase item to a new list
3. Output the new list when the loop completes

```
[Array Input] → [For Loop] → [Completed] → [Get Variable: "uppercase_items"] → [Array Output]
                    ↓
                [Current Item] → [String: "uppercase"] → [Set Variable: "current_uppercase"]
```

## Best Practices

1. **Use Meaningful Variable Names**: Choose descriptive names for your variables to make your workflow easier to understand.

2. **Limit Loop Iterations**: Always set a reasonable maximum number of iterations for while loops to prevent infinite loops.

3. **Use Variables for Complex Data**: Store complex data structures (arrays, objects) in variables rather than passing them directly between nodes.

4. **Clean Up Variables**: Consider clearing variables that are no longer needed, especially if they contain large amounts of data.

5. **Use Conditionals for Error Handling**: Use conditional nodes to handle errors and edge cases in your workflow.

6. **Collect Results When Needed**: Only enable result collection in loops when you actually need the results, as it can consume memory for large datasets.

7. **Use Loop Variables**: Take advantage of the automatic loop variables (item_variable, index_variable) to simplify your workflow.

8. **Prefer For Loops for Known Iterations**: Use for loops when you know the number of iterations in advance, and while loops when the number of iterations depends on a condition.
