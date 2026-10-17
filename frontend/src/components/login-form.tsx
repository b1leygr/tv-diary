import { Anchor, Text } from '@mantine/core';
import { useForm } from '@mantine/form';
import { useMutation } from '@tanstack/react-query';
import { Link, useNavigate } from '@tanstack/react-router';
import { toast } from 'react-hot-toast';
import { type BodyLogin, login } from '#/client';
import { UserForm } from './user-form';

export function LoginForm() {
  const form = useForm({
    initialValues: {
      username: '',
      password: '',
    },
  });

  const navigate = useNavigate();

  const {
    mutate: loginMutation,
    error: loginError,
    isPending: loginPending,
  } = useMutation({
    mutationFn: (credentials: BodyLogin) => login({ body: credentials }),
    onSuccess: ({ data }) => {
      localStorage.setItem('token', data?.access_token || '');
      console.log('Login successful, token stored:', data?.access_token);
      toast.success('Login successful!');
      navigate({ to: '/search', search: { query: '' } });
    },
    onError: (error) => {
      console.error('Login failed:', error);
      toast.error(loginError?.detail || 'Login failed!');
    },
  });

  const handleSubmit = (values: typeof form.values) => {
    const { username, password } = values;
    loginMutation({ username, password });
  };

  return (
    <UserForm
      form={form}
      onSubmit={form.onSubmit(handleSubmit)}
      pending={loginPending}
      submitLabel="Login"
      extra={
        <Text mt="md" ta="center" size="sm">
          Don't have an account?{' '}
          <Anchor component={Link} to="/signup">
            Sign up
          </Anchor>
        </Text>
      }
    />
  );
}
