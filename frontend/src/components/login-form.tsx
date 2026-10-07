import {
  Anchor,
  Button,
  Container,
  Paper,
  PasswordInput,
  Text,
  TextInput,
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { useMutation } from '@tanstack/react-query';
import { Link } from '@tanstack/react-router';
import { type BodyLogin, login } from '#/client';

export function LoginForm() {
  const form = useForm({
    initialValues: {
      username: '',
      password: '',
    },
  });

  const loginMutation = useMutation({
    mutationFn: (credentials: BodyLogin) => login({ body: credentials }),
    onSuccess: ({ data }) => {
      localStorage.setItem('token', data?.access_token || '');
      console.log('Login successful, token stored:', data?.access_token);
    },
    onError: (error) => {
      console.error('Login failed:', error);
    },
  });

  const handleSubmit = (values: typeof form.values) => {
    const { username, password } = values;
    loginMutation.mutate({ username, password });
  };

  return (
    <Container size={420} my={40}>
      <Paper withBorder shadow="md" p={30} mt={30} radius={'md'}>
        <form onSubmit={form.onSubmit(handleSubmit)}>
          <TextInput
            label="username"
            placeholder="johndoe"
            required
            {...form.getInputProps('username')}
          />
          <PasswordInput
            label="password"
            placeholder="password"
            required
            mt="md"
            {...form.getInputProps('password')}
          />
          <Button
            type="submit"
            fullWidth
            mt="md"
            loading={loginMutation.isPending}
          >
            Login
          </Button>
          <Text mt="md" ta="center" size="sm">
            Don't have an account?{' '}
            <Anchor component={Link} to="/signup">
              Sign up
            </Anchor>
          </Text>
        </form>
      </Paper>
    </Container>
  );
}
