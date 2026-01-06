import {
  ValidatorConstraint,
  ValidatorConstraintInterface,
  ValidationArguments,
  registerDecorator,
  ValidationOptions
} from "class-validator";

@ValidatorConstraint({ name: "StrongPassword", async: false })
export class StrongPasswordValidator implements ValidatorConstraintInterface {
  validate(value: string) {
    if (typeof value !== "string") return false;
    // 至少10位，包含数字、大小写字母、特殊字符
    const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{10,}$/;
    return regex.test(value);
  }

  defaultMessage(args: ValidationArguments) {
    return "密码至少10位，包含数字、大小写字母、特殊字符";
  }
}


export function IsStrongPassword(validationOptions?: ValidationOptions) {
  return function (object: any, propertyName: string) {
    registerDecorator({
      name: "IsStrongPassword",
      target: object.constructor,
      propertyName,
      options: validationOptions,
      validator: StrongPasswordValidator,
    });
  };
}