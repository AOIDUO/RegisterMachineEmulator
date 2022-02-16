from __future__ import annotations

from dataclasses import dataclass
from typing import Union, List, Optional, Type
from xdsl.dialects.builtin import StringAttr, IntegerAttr
from xdsl.irdl import irdl_op_definition, AttributeDef, \
    SingleBlockRegionDef, AnyOf, irdl_attr_definition, builder
from xdsl.ir import Operation, MLContext, Data, ParametrizedAttribute

from xdsl.parser import Parser
from xdsl.printer import Printer


@irdl_op_definition
class Program(Operation):
    name = "choco.ast.program"

    # [VarDef | FuncDef]*
    defs = SingleBlockRegionDef()

    # Stmt*
    stmts = SingleBlockRegionDef()

    @staticmethod
    def get(defs: List[Operation],
            stmts: List[Operation],
            verify_op: bool = True) -> Program:
        res = Program.build(regions=[defs, stmts])
        if verify_op:
            # We don't verify nested operations since they might have already been verified
            res.verify(verify_nested_ops=False)
        return res

    def verify_(self) -> None:
        for def_ in self.defs.blocks[0].ops:
            if type(def_) not in [VarDef, FuncDef]:
                raise Exception(
                    f"{Program.name} first region expects {VarDef.name} "
                    f"and {FuncDef.name} operations, but got {def_.name}")
        for stmt in self.stmts.blocks[0].ops:
            if type(stmt) not in ChocoAST.get_statement_op_types():
                raise Exception(f"{Program.name} second region only expects "
                                f"statements operations, but got {stmt.name}")


@irdl_op_definition
class FuncDef(Operation):
    name = "choco.ast.func_def"

    func_name = AttributeDef(StringAttr)
    params = SingleBlockRegionDef()
    return_type = SingleBlockRegionDef()

    # [GlobalDecl | NonLocalDecl | VarDef ]* Stmt+
    func_body = SingleBlockRegionDef()

    @staticmethod
    def get(func_name: Union[str, StringAttr],
            params: List[Operation],
            return_type: Operation,
            func_body: List[Operation],
            verify_op: bool = True) -> FuncDef:
        res = FuncDef.build(attributes={"func_name": func_name},
                            regions=[params, [return_type], func_body])
        if verify_op:
            # We don't verify nested operations since they might have already been verified
            res.verify(verify_nested_ops=False)
        return res

    def verify_(self) -> None:
        for param in self.params.blocks[0].ops:
            if not isinstance(param, TypedVar):
                raise Exception(
                    f"{FuncDef.name} first region expects {TypedVar.name} "
                    f"operations, but got {param.name}.")
        return_type = self.return_type.blocks[0].ops
        if len(return_type) != 1:
            raise Exception(f"{FuncDef.name} expects a single return type")
        if type(return_type[0]) not in ChocoAST.get_type_op_types():
            raise Exception(
                f"{FuncDef.name} second region expects a single operation "
                f"representing a type, but got {return_type[0].name}.")
        stmt_region = False
        for stmt in self.func_body.blocks[0].ops:
            if not stmt_region:
                if type(stmt) in [GlobalDecl, NonLocalDecl, VarDef]:
                    continue
                else:
                    stmt_region = True
            if stmt_region:
                if not type(stmt) in ChocoAST.get_statement_op_types():
                    raise Exception(
                        f"{FuncDef.name} third region expects variable declarations "
                        f"followed by statements, but got {stmt.name}")


@irdl_op_definition
class TypedVar(Operation):
    name = "choco.ast.typed_var"

    var_name = AttributeDef(StringAttr)
    type = SingleBlockRegionDef()

    @staticmethod
    def get(var_name: str,
            type: Operation,
            verify_op: bool = True) -> TypedVar:
        res = TypedVar.build(regions=[[type]],
                             attributes={"var_name": var_name})
        if verify_op:
            # We don't verify nested operations since they might have already been verified
            res.verify(verify_nested_ops=False)
        return res

    def verify_(self) -> None:
        typ = self.type.blocks[0].ops
        if len(typ) != 1 or type(typ[0]) not in ChocoAST.get_type_op_types():
            raise Exception(
                f"{TypedVar.name} second region expects a single operation representing a type, but got {typ}."
            )


@irdl_op_definition
class TypeName(Operation):
    name = "choco.ast.type_name"

    type_name = AttributeDef(StringAttr)

    @staticmethod
    def get(type_name: Union[str, StringAttr],
            verify_op: bool = True) -> TypeName:
        res = TypeName.build(attributes={"type_name": type_name})
        if verify_op:
            # We don't verify nested operations since they might have already been verified
            res.verify(verify_nested_ops=False)
        return res

    def verify_(self) -> None:
        legal_type_names = ["object", "int", "bool", "str", "<None>"]
        if self.type_name.data not in legal_type_names:
            raise Exception(
                f"{self.name} expects type name, but got '{self.type_name.data}'"
            )


@irdl_op_definition
class ListType(Operation):
    name = "choco.ast.list_type"

    elem_type = SingleBlockRegionDef()

    @staticmethod
    def get(elem_type: Operation, verify_op: bool = True) -> ListType:
        res = ListType.build(regions=[[elem_type]])
        if verify_op:
            # We don't verify nested operations since they might have already been verified
            res.verify(verify_nested_ops=False)
        return res

    def verify_(self) -> None:
        elem_type = self.elem_type.blocks[0].ops
        if len(elem_type) != 1 or type(
                elem_type[0]) not in ChocoAST.get_type_op_types():
            raise Exception(
                f"{ListType.name} operation expects a single type operation in the first region."
            )


@irdl_op_definition
class GlobalDecl(Operation):
    name = "choco.ast.global_decl"

    decl_name = AttributeDef(StringAttr)

    @staticmethod
    def get(decl_name: Union[str, StringAttr],
            verify_op: bool = True) -> GlobalDecl:
        res = GlobalDecl.build(attributes={"decl_name": decl_name})
        if verify_op:
            # We don't verify nested operations since they might have already been verified
            res.verify(verify_nested_ops=False)
        return res


@irdl_op_definition
class NonLocalDecl(Operation):
    name = "choco.ast.nonlocal_decl"

    decl_name = AttributeDef(StringAttr)

    @staticmethod
    def get(decl_name: Union[str, StringAttr],
            verify_op: bool = True) -> NonLocalDecl:
        res = NonLocalDecl.build(attributes={"decl_name": decl_name})
        if verify_op:
            # We don't verify nested operations since they might have already been verified
            res.verify(verify_nested_ops=False)
        return res


@irdl_op_definition
class VarDef(Operation):
    name = "choco.ast.var_def"

    typed_var = SingleBlockRegionDef()
    literal = SingleBlockRegionDef()

    @staticmethod
    def get(typed_var: Operation,
            literal: Operation,
            verify_op: bool = True) -> VarDef:
        res = VarDef.build(regions=[[typed_var], [literal]])
        if verify_op:
            # We don't verify nested operations since they might have already been verified
            res.verify(verify_nested_ops=False)
        return res

    def verify_(self) -> None:
        elem_type = self.typed_var.blocks[0].ops
        if len(elem_type) != 1 or not isinstance(elem_type[0], TypedVar):
            raise Exception(
                f"{VarDef.name} operation expects a single {TypedVar.name} operation in the first region."
            )
        literal = self.literal.blocks[0].ops
        if len(literal) != 1 or not isinstance(literal[0], Literal):
            raise Exception(
                f"{VarDef.name} operation expects a single {Literal.name} operation in the second region."
            )


# Statements


@irdl_op_definition
class If(Operation):
    name = "choco.ast.if"

    cond = SingleBlockRegionDef()
    then = SingleBlockRegionDef()
    orelse = SingleBlockRegionDef()

    @staticmethod
    def get(cond: Operation,
            then: List[Operation],
            orelse: List[Operation],
            verify_op: bool = True) -> If:
        res = If.build(regions=[[cond], then, orelse])
        if verify_op:
            # We don't verify nested operations since they might have already been verified
            res.verify(verify_nested_ops=False)
        return res

    def verify_(self) -> None:
        cond = self.cond.blocks[0].ops
        if len(cond) != 1 or type(
                cond[0]) not in ChocoAST.get_expression_op_types():
            raise Exception(
                f"{If.name} operation expects a single expression in the first region."
            )
        for expr in self.then.blocks[0].ops:
            if type(expr) not in ChocoAST.get_statement_op_types():
                raise Exception(
                    f"{If.name} operation expects statements operations in the second region."
                )
        for expr in self.orelse.blocks[0].ops:
            if type(expr) not in ChocoAST.get_statement_op_types():
                raise Exception(
                    f"{If.name} operation expects statements operations in the third region."
                )


@irdl_op_definition
class While(Operation):
    name = "choco.ast.while"

    cond = SingleBlockRegionDef()
    body = SingleBlockRegionDef()

    @staticmethod
    def get(cond: Operation,
            body: List[Operation],
            verify_op: bool = True) -> While:
        res = While.build(regions=[[cond], body])
        if verify_op:
            # We don't verify nested operations since they might have already been verified
            res.verify(verify_nested_ops=False)
        return res

    def verify_(self) -> None:
        cond = self.cond.blocks[0].ops
        if len(cond) != 1 or type(
                cond[0]) not in ChocoAST.get_expression_op_types():
            raise Exception(
                f"{While.name} operation expects a single expression in the first region."
            )
        for stmt in self.body.blocks[0].ops:
            if type(stmt) not in ChocoAST.get_statement_op_types():
                raise Exception(
                    f"{While.name} operation expects statements operations in the second region."
                )


@irdl_op_definition
class For(Operation):
    name = "choco.ast.for"

    iter_name = AttributeDef(StringAttr)
    iter = SingleBlockRegionDef()
    body = SingleBlockRegionDef()

    @staticmethod
    def get(iter_name: Union[str, StringAttr],
            iter: Operation,
            body: List[Operation],
            verify_op: bool = True) -> For:
        res = For.build(attributes={"iter_name": iter_name},
                        regions=[[iter], body])
        if verify_op:
            # We don't verify nested operations since they might have already been verified
            res.verify(verify_nested_ops=False)
        return res

    def verify_(self) -> None:
        iter = self.iter.blocks[0].ops
        if len(iter) != 1 or type(
                iter[0]) not in ChocoAST.get_expression_op_types():
            raise Exception(
                f"{For.name} operation expects a single expression in the first region."
            )
        for stmt in self.body.blocks[0].ops:
            if type(stmt) not in ChocoAST.get_statement_op_types():
                raise Exception(
                    f"{For.name} operation expects statements operations in the second region."
                )


@irdl_op_definition
class Pass(Operation):
    name = "choco.ast.pass"

    @staticmethod
    def get() -> Pass:
        return Pass.create()


@irdl_op_definition
class Return(Operation):
    name = "choco.ast.return"

    value = SingleBlockRegionDef()

    @staticmethod
    def get(value: Optional[Operation], verify_op: bool = True) -> Return:
        res = Return.build(regions=[[value] if value is not None else []])
        if verify_op:
            # We don't verify nested operations since they might have already been verified
            res.verify(verify_nested_ops=False)
        return res

    def verify_(self) -> None:
        value = self.value.blocks[0].ops
        if len(value) > 1 or (len(value) == 1 and type(value[0])
                              not in ChocoAST.get_expression_op_types()):
            raise Exception(
                f"{Return.name} operation expects a single expression in the first region."
            )


@irdl_op_definition
class Assign(Operation):
    name = "choco.ast.assign"

    target = SingleBlockRegionDef()
    value = SingleBlockRegionDef()

    @staticmethod
    def get(target: Operation,
            value: Operation,
            verify_op: bool = True) -> Assign:
        res = Assign.build(regions=[[target], [value]])
        if verify_op:
            # We don't verify nested operations since they might have already been verified
            res.verify(verify_nested_ops=False)
        return res

    def verify_(self) -> None:
        target = self.target.blocks[0].ops
        if len(target) != 1 or type(
                target[0]) not in ChocoAST.get_expression_op_types():
            raise Exception(
                f"{Assign.name} operation expects a single expression in the first region, but get {target}."
            )
        for expr in self.value.blocks[0].ops:
            if type(expr) not in ChocoAST.get_expression_op_types() + [Assign]:
                raise Exception(
                    f"{Assign.name} operation expects a single expression, or a single {Assign.name} operation in the second region."
                )


# Expressions


@irdl_attr_definition
class BoolAttr(Data):
    name = 'choco.ast.bool'
    data: bool

    @staticmethod
    def parse(parser: Parser) -> Data:
        val = parser.parse_while(lambda char: char != '>')
        if val == "True":
            return BoolAttr(True)  # type: ignore
        if val == "False":
            return BoolAttr(False)  # type: ignore
        raise Exception(f"Unexpected BoolAttr value: '{val}'.")

    def print(self, printer: Printer) -> None:
        if self.data:
            printer.print_string("True")
        else:
            printer.print_string("False")

    @staticmethod
    @builder
    def from_bool(val: bool) -> BoolAttr:
        return BoolAttr(val)  # type: ignore


@irdl_attr_definition
class NoneAttr(ParametrizedAttribute):
    name = 'choco.ast.none'


@irdl_op_definition
class Literal(Operation):
    name = "choco.ast.literal"

    value = AttributeDef(AnyOf([StringAttr, IntegerAttr, BoolAttr, NoneAttr]))

    @staticmethod
    def get(value: Union[None, bool, int, str],
            verify_op: bool = True) -> Literal:
        if value is None:
            attr = NoneAttr()
        elif type(value) is bool:
            attr = BoolAttr.from_bool(value)
        elif type(value) is int:
            attr = IntegerAttr.from_int_and_width(value, 32)
        elif type(value) is str:
            attr = StringAttr.from_str(value)
        else:
            raise Exception(f"Unknown literal of type {type(value)}")
        res = Literal.create(attributes={"value": attr})
        if verify_op:
            # We don't verify nested operations since they might have already been verified
            res.verify(verify_nested_ops=False)
        return res


@irdl_op_definition
class ExprName(Operation):
    name = "choco.ast.id_expr"

    id = AttributeDef(StringAttr)

    @staticmethod
    def get(name: Union[str, StringAttr], verify_op: bool = True) -> ExprName:
        res = ExprName.build(attributes={"id": name})
        if verify_op:
            # We don't verify nested operations since they might have already been verified
            res.verify(verify_nested_ops=False)
        return res


@irdl_op_definition
class UnaryExpr(Operation):
    name = "choco.ast.unary_expr"

    op = AttributeDef(StringAttr)
    value = SingleBlockRegionDef()

    @staticmethod
    def get_valid_ops() -> List[str]:
        return ["-", "not"]

    @staticmethod
    def get(op: Union[str, StringAttr],
            value: Operation,
            verify_op: bool = True) -> UnaryExpr:
        res = UnaryExpr.build(attributes={"op": op}, regions=[[value]])
        if verify_op:
            # We don't verify nested operations since they might have already been verified
            res.verify(verify_nested_ops=False)
        return res

    def verify_(self) -> None:
        if self.op.data not in self.get_valid_ops():
            raise Exception(f"Unsupported unary expression: '{self.op.data}'.")
        value = self.value.blocks[0].ops
        if len(value) != 1 or type(
                value[0]) not in ChocoAST.get_expression_op_types():
            raise Exception(
                f"{UnaryExpr.name} operation expects a single expression in the first region."
            )


@irdl_op_definition
class BinaryExpr(Operation):
    name = "choco.ast.binary_expr"

    op = AttributeDef(StringAttr)
    lhs = SingleBlockRegionDef()
    rhs = SingleBlockRegionDef()

    @staticmethod
    def get_valid_ops() -> List[str]:
        return [
            "+", "-", "*", "//", "%", "and", "is", "or", ">", "<", "==", "!=",
            ">=", "<="
        ]

    @staticmethod
    def get(op: str,
            lhs: Operation,
            rhs: Operation,
            verify_op: bool = True) -> BinaryExpr:
        res = BinaryExpr.build(attributes={"op": op}, regions=[[lhs], [rhs]])
        if verify_op:
            # We don't verify nested operations since they might have already been verified
            res.verify(verify_nested_ops=False)
        return res

    def verify_(self) -> None:
        if self.op.data not in self.get_valid_ops():
            raise Exception(f"Unsupported unary expression: '{self.op.data}'.")
        lhs = self.lhs.blocks[0].ops
        if len(lhs) != 1 or type(
                lhs[0]) not in ChocoAST.get_expression_op_types():
            raise Exception(
                f"{BinaryExpr.name} operation expects a single expression in the first region."
            )
        rhs = self.rhs.blocks[0].ops
        if len(rhs) != 1 or type(
                rhs[0]) not in ChocoAST.get_expression_op_types():
            raise Exception(
                f"{BinaryExpr.name} operation expects a single expression in the second region."
            )


@irdl_op_definition
class IfExpr(Operation):
    name = "choco.ast.if_expr"

    cond = SingleBlockRegionDef()
    then = SingleBlockRegionDef()
    or_else = SingleBlockRegionDef()

    @staticmethod
    def get(cond: Operation,
            then: Operation,
            or_else: Operation,
            verify_op: bool = True) -> IfExpr:
        res = IfExpr.build(regions=[[cond], [then], [or_else]])
        if verify_op:
            # We don't verify nested operations since they might have already been verified
            res.verify(verify_nested_ops=False)
        return res

    def verify_(self) -> None:
        cond = self.cond.blocks[0].ops
        if len(cond) != 1 or type(
                cond[0]) not in ChocoAST.get_expression_op_types():
            raise Exception(
                f"{IfExpr.name} operation expects a single expression in the first region."
            )
        then = self.then.blocks[0].ops
        if len(then) != 1 or type(
                then[0]) not in ChocoAST.get_expression_op_types():
            raise Exception(
                f"{IfExpr.name} operation expects a single expression in the second region."
            )
        or_else = self.or_else.blocks[0].ops
        if len(or_else) != 1 or type(
                or_else[0]) not in ChocoAST.get_expression_op_types():
            raise Exception(
                f"{IfExpr.name} operation expects a single expression in the third region."
            )


@irdl_op_definition
class ListExpr(Operation):
    name = "choco.ast.list_expr"

    elems = SingleBlockRegionDef()

    @staticmethod
    def get(elems: List[Operation], verify_op: bool = True) -> ListExpr:
        res = ListExpr.build(regions=[elems])
        if verify_op:
            # We don't verify nested operations since they might have already been verified
            res.verify(verify_nested_ops=False)
        return res

    def verify_(self) -> None:
        for expr in self.elems.blocks[0].ops:
            if type(expr) not in ChocoAST.get_expression_op_types():
                raise Exception(
                    f"{ListExpr.name} operation expects expression operations in the first region."
                )


@irdl_op_definition
class CallExpr(Operation):
    name = "choco.ast.call_expr"

    func = AttributeDef(StringAttr)
    args = SingleBlockRegionDef()

    @staticmethod
    def get(func: str,
            args: List[Operation],
            verify_op: bool = True) -> CallExpr:
        res = CallExpr.build(regions=[args], attributes={"func": func})
        if verify_op:
            # We don't verify nested operations since they might have already been verified
            res.verify(verify_nested_ops=False)
        return res

    def verify_(self) -> None:
        for arg in self.args.blocks[0].ops:
            if type(arg) not in ChocoAST.get_expression_op_types():
                raise Exception(
                    f"{CallExpr.name} operation expects expression operations in the second region."
                )


@irdl_op_definition
class IndexExpr(Operation):
    name = "choco.ast.index_expr"

    value = SingleBlockRegionDef()
    index = SingleBlockRegionDef()

    @staticmethod
    def get(value: Operation,
            index: Operation,
            verify_op: bool = True) -> IndexExpr:
        res = IndexExpr.build(regions=[[value], [index]])
        if verify_op:
            # We don't verify nested operations since they might have already been verified
            res.verify(verify_nested_ops=False)
        return res

    def verify_(self) -> None:
        value = self.value.blocks[0].ops
        if len(value) != 1 or type(
                value[0]) not in ChocoAST.get_expression_op_types():
            raise Exception(
                f"{IndexExpr.name} operation expects a single expression operation in the first region."
            )
        index = self.index.blocks[0].ops
        if len(index) != 1 or type(
                index[0]) not in ChocoAST.get_expression_op_types():
            raise Exception(
                f"{IndexExpr.name} operation expects a single expression operation in the first region."
            )


@dataclass
class ChocoAST:
    ctx: MLContext

    def __post_init__(self):
        self.ctx.register_attr(NoneAttr)
        self.ctx.register_attr(BoolAttr)

        self.ctx.register_op(Program)
        self.ctx.register_op(FuncDef)
        self.ctx.register_op(TypedVar)
        self.ctx.register_op(TypeName)
        self.ctx.register_op(ListType)
        self.ctx.register_op(GlobalDecl)
        self.ctx.register_op(NonLocalDecl)
        self.ctx.register_op(VarDef)
        self.ctx.register_op(If)
        self.ctx.register_op(While)
        self.ctx.register_op(For)
        self.ctx.register_op(Pass)
        self.ctx.register_op(Return)
        self.ctx.register_op(Assign)
        self.ctx.register_op(Literal)
        self.ctx.register_op(ExprName)
        self.ctx.register_op(UnaryExpr)
        self.ctx.register_op(BinaryExpr)
        self.ctx.register_op(IfExpr)
        self.ctx.register_op(ListExpr)
        self.ctx.register_op(CallExpr)
        self.ctx.register_op(IndexExpr)

    @staticmethod
    def get_type(annotation: str) -> Operation:
        return TypeName.get(annotation)

    @staticmethod
    def get_statement_op_types() -> List[Type[Operation]]:
        statements: List[Type[Operation]] = [
            If, While, For, Pass, Return, Assign
        ]
        return statements + ChocoAST.get_expression_op_types()

    @staticmethod
    def get_expression_op_types() -> List[Type[Operation]]:
        return [
            UnaryExpr, BinaryExpr, IfExpr, ExprName, ListExpr, IndexExpr,
            CallExpr, Literal
        ]

    @staticmethod
    def get_type_op_types() -> List[Type[Operation]]:
        return [TypeName, ListType]
