import {
  Button,
  Container,
  Paper,
  PasswordInput,
  TextInput,
} from '@mantine/core';
import type { UseFormReturnType } from '@mantine/form';
import type { ValidationErrorDetail } from '#/client';

interface UserFormProps {
  form: UseFormReturnType<{
    [key: string]: string;
  }>;
  onSubmit: () => void;
  pending: boolean;
  submitLabel: string;
  usernameErrors?: ValidationErrorDetail[];
  passwordErrors?: ValidationErrorDetail[];
  extra?: React.ReactNode;
}

export function UserForm({
  form,
  onSubmit,
  pending,
  submitLabel,
  usernameErrors,
  passwordErrors,
  extra,
}: UserFormProps) {
  return (
    <Container size={420} my={40}>
      <Paper withBorder shadow="md" p={30} mt={30} radius="md">
        <form onSubmit={onSubmit}>
          <TextInput
            label="username"
            placeholder="johndoe"
            required
            {...form.getInputProps('username')}
          />
          {usernameErrors && (
            <div style={{ color: 'red', marginTop: '5px' }}>
              {usernameErrors.map((error) => (
                <div key={error.reason}>{error.reason}</div>
              ))}
            </div>
          )}
          <PasswordInput
            label="password"
            placeholder="password"
            required
            mt="md"
            {...form.getInputProps('password')}
          />
          {passwordErrors && (
            <div style={{ color: 'red', marginTop: '5px' }}>
              {passwordErrors.map((error) => (
                <div key={error.reason}>{error.reason}</div>
              ))}
            </div>
          )}
          <Button type="submit" fullWidth mt="md" loading={pending}>
            {submitLabel}
          </Button>
          {extra}
        </form>
      </Paper>
    </Container>
  );
}
