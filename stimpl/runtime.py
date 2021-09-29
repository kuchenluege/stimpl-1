from . import *

"""
Interpreter State
"""
class State(object):
  def __init__(self):
    self.state = {}
    pass

  def set_value(self, variable_name, variable_value, variable_type):
    new_state = State()
    for k, v in self.state.items():
      new_state.state[k] = v

    new_state.state[variable_name] = (variable_value, variable_type)
    return new_state


  def get_value(self, variable_name):
    try:
      return self.state[variable_name]
    except KeyError:
      return None

  def __repr__(self):
    result = ""
    for k, v in self.state.items():
      result += f"\n{k}: {v}"
    return result

"""
Main evaluation logic!
"""
def evaluate(expression, state):
  match expression:
    case Ren():
      return (None, Unit(), state)

    case IntLiteral(literal=l):
      return (l, Integer(), state)

    case FloatingPointLiteral(literal=l):
      return (l, FloatingPoint(), state)

    case StringLiteral(literal=l):
      return (l, String(), state)

    case BooleanLiteral(literal=l):
      return (l, Boolean(), state)

    case Print(to_print=to_print):
      printable_value, printable_type, new_state = evaluate(to_print, state)

      if isinstance(printable_type,Unit):
        print("Unit")
      else:
        print(f"{printable_value}")

      return (printable_value, printable_type, new_state)

    case Variable(variable_name=variable_name):
      value = state.get_value(variable_name)
      if value == None:
        raise InterpSyntaxError(f"Cannot read from {variable_name} before assignment.")
      return (*value, state)

    case Sequence(exprs = exprs) | Program(exprs = exprs):
      if len(exprs) == 0:
        return evaluate(Ren(), state)
      value_result, value_type, new_state = evaluate(exprs[0], state)
      if len(exprs) == 1:
        return (value_result, value_type, new_state)
      return evaluate(Sequence(*exprs[1:]), new_state)

    case Assign(variable=variable, value=value):

      value_result, value_type, new_state = evaluate(value, state)

      variable_from_state = new_state.get_value(variable.variable_name)
      _, variable_type = variable_from_state if variable_from_state else (None, None)

      if value_type != variable_type and variable_type != None:
        raise InterpTypeError(f"""Mismatched types for Assignment: 
            Cannot assign {value_type} to {variable_type}""")

      new_state = new_state.set_value(variable.variable_name, value_result, value_type)
      return (value_result, value_type, new_state)

    case Add(left=left, right=right):
      result = 0
      left_result, left_type, new_state = evaluate(left, state)
      right_result, right_type, new_state = evaluate(right, new_state)

      if left_type != right_type:
        raise InterpTypeError(f"""Mismatched types for Add: 
            Cannot add {left_type} to {right_type}""")
      
      match left_type:
        case Integer() | String() | FloatingPoint():
          result = left_result + right_result
        case _:
          raise InterpTypeError(f"""Cannot add {left_type}s""")

      return (result, left_type, new_state)

    case Subtract(left=left, right=right):
      result = 0
      left_result, left_type, new_state = evaluate(left, state)
      right_result, right_type, new_state = evaluate(right, new_state)

      if left_type != right_type:
        raise InterpTypeError(f"""Mismatched types for Subtract: 
            Cannot subtract {right_type} from {left_type}""")
      
      match left_type:
        case Integer() |  FloatingPoint():
          result = left_result - right_result
        case _:
          raise InterpTypeError(f"""Cannot subtract {left_type}s""")

      return (result, left_type, new_state)

    case Multiply(left=left, right=right):
      result = 0
      left_result, left_type, new_state = evaluate(left, state)
      right_result, right_type, new_state = evaluate(right, new_state)

      if left_type != right_type:
        raise InterpTypeError(f"""Mismatched types for Multiply: 
            Cannot multiply {left_type} and {right_type}""")
      
      match left_type:
        case Integer() |  FloatingPoint():
          result = left_result * right_result
        case _:
          raise InterpTypeError(f"""Cannot multiply {left_type}s""")

      return (result, left_type, new_state)

    case Divide(left=left, right=right):
      result = 0
      left_result, left_type, new_state = evaluate(left, state)
      right_result, right_type, new_state = evaluate(right, new_state)

      if left_type != right_type:
        raise InterpTypeError(f"""Mismatched types for Divide: 
            Cannot divide {left_type} by {right_type}""")
      
      match left_type:
        case Integer():
          result = left_result // right_result
        case FloatingPoint():
          result = left_result / right_result
        case _:
          raise InterpTypeError(f"""Cannot divide {left_type}s""")

      return (result, left_type, new_state)

    case And(left=left, right=right):
      left_value, left_type, new_state = evaluate(left, state)
      right_value, right_type, new_state = evaluate(right, new_state)

      if left_type != right_type:
        raise InterpTypeError(f"""Mismatched types for And: 
            Cannot perform logical and on {left_type} and {right_type}""")
      match left_type:
        case Boolean():
          result = left_value and right_value
        case _:
          raise InterpTypeError("Cannot perform logical and on non-boolean operands.")
 
      return (result, left_type, new_state)

    case Or(left=left, right=right):
      left_value, left_type, new_state = evaluate(left, state)
      right_value, right_type, new_state = evaluate(right, new_state)

      if left_type != right_type:
        raise InterpTypeError(f"""Mismatched types for Or: 
            Cannot perform logical or on {left_type} and {right_type}""")
      match left_type:
        case Boolean():
          result = left_value or right_value
        case _:
          raise InterpTypeError("Cannot perform logical or on non-boolean operands.")
 
      return (result, left_type, new_state)

    case Not(expr=expr):
      expr_result, expr_type, new_state = evaluate(expr, state)

      match expr_type:
        case Boolean():
          result = not(expr_result)
        case _:
          raise InterpTypeError("Cannot perform logical not on a non-boolean operand.")

      return (result, expr_type, new_state)

    case If(condition=condition, true=true, false=false):
      cond_result, cond_type, new_state = evaluate(condition, state)

      match cond_type:
        case Boolean():
          result = cond_result
        case _:
          raise InterpTypeError("If statement requires a boolean condition.")

      if result:
        return evaluate(true, new_state)
      return evaluate(false, new_state)

    case Lt(left=left, right=right):
      left_value, left_type, new_state = evaluate(left, state)
      right_value, right_type, new_state = evaluate(right, new_state)

      result = None

      if left_type != right_type:
        raise InterpTypeError(f"""Mismatched types for Lt: 
            Cannot compare {left_type} to {right_type}""")

      match left_type:
        case Integer() | Boolean() | String() | FloatingPoint():
          result = left_value < right_value
        case Unit():
          result = False
        case _:
          raise InterpTypeError(f"Cannot perform < on {left_type} type.")

      return (result, Boolean(), new_state)

    case Lte(left=left, right=right):
      left_value, left_type, new_state = evaluate(left, state)
      right_value, right_type, new_state = evaluate(right, new_state)

      result = None

      if left_type != right_type:
        raise InterpTypeError(f"""Mismatched types for Lte: 
            Cannot compare {left_type} to {right_type}""")

      match left_type:
        case Integer() | Boolean() | String() | FloatingPoint():
          result = left_value <= right_value
        case Unit():
          result = True
        case _:
          raise InterpTypeError(f"Cannot perform <= on {left_type} type.")

      return (result, Boolean(), new_state)

    case Gt(left=left, right=right):
      left_value, left_type, new_state = evaluate(left, state)
      right_value, right_type, new_state = evaluate(right, new_state)

      result = None

      if left_type != right_type:
        raise InterpTypeError(f"""Mismatched types for Gt: 
            Cannot compare {left_type} to {right_type}""")

      match left_type:
        case Integer() | Boolean() | String() | FloatingPoint():
          result = left_value > right_value
        case Unit():
          result = False
        case _:
          raise InterpTypeError(f"Cannot perform > on {left_type} type.")

      return (result, Boolean(), new_state)

    case Gte(left=left, right=right):
      left_value, left_type, new_state = evaluate(left, state)
      right_value, right_type, new_state = evaluate(right, new_state)

      result = None

      if left_type != right_type:
        raise InterpTypeError(f"""Mismatched types for Gte: 
            Cannot compare {left_type} to {right_type}""")

      match left_type:
        case Integer() | Boolean() | String() | FloatingPoint():
          result = left_value >= right_value
        case Unit():
          result = True
        case _:
          raise InterpTypeError(f"Cannot perform >= on {left_type} type.")

      return (result, Boolean(), new_state)

    case Eq(left=left, right=right):
      left_value, left_type, new_state = evaluate(left, state)
      right_value, right_type, new_state = evaluate(right, new_state)

      result = None

      if left_type != right_type:
        raise InterpTypeError(f"""Mismatched types for Eq: 
            Cannot compare {left_type} to {right_type}""")

      match left_type:
        case Integer() | Boolean() | String() | FloatingPoint():
          result = left_value == right_value
        case Unit():
          result = True
        case _:
          raise InterpTypeError(f"Cannot perform == on {left_type} type.")

      return (result, Boolean(), new_state)

    case Ne(left=left, right=right):
      left_value, left_type, new_state = evaluate(left, state)
      right_value, right_type, new_state = evaluate(right, new_state)

      result = None

      if left_type != right_type:
        raise InterpTypeError(f"""Mismatched types for Ne: 
            Cannot compare {left_type} to {right_type}""")

      match left_type:
        case Integer() | Boolean() | String() | FloatingPoint():
          result = left_value != right_value
        case Unit():
          result = False
        case _:
          raise InterpTypeError(f"Cannot perform != on {left_type} type.")

      return (result, Boolean(), new_state)

    case While(condition=condition, body=body):
      cond_result, cond_type, new_state = evaluate(condition, state)

      match cond_type:
        case Boolean():
          result = cond_result
        case _:
          raise InterpTypeError("While loop requires a boolean condition.")

      while result:
        body_result, body_type, new_state = evaluate(body, new_state)
        cond_result, cond_type, new_state = evaluate(condition, new_state)

        match cond_type:
          case Boolean():
            result = cond_result
          case _:
            raise InterpTypeError("While loop requires a boolean condition.")

      return (result, body_type, new_state)

    case _:
      raise InterpSyntaxError("Unhandled!")
  pass

def run_stimpl(program, debug=False):
  state = State()

  program_value, program_type, program_state = evaluate(program, state)

  if debug:
    print(f"program: {program}")
    print(f"final_value: ({program_value}, {program_type})")
    print(f"final_state: {program_state}")

  return program_value, program_type, program_state
