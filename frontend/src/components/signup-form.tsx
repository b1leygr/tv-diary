import { Anchor, Text } from '@mantine/core';
import { useForm } from '@mantine/form';
import { useMutation } from '@tanstack/react-query';
import { Link, useNavigate } from '@tanstack/react-router';
import { toast } from 'react-hot-toast';
import { createUser, type UserCreate } from '#/client';
import { UserForm } from './user-form';

export function SignupForm() {
  const form = useForm({
    initialValues: {
      username: '',
      password: '',
    },
  });
  const navigate = useNavigate();

  const {
    mutate: signUpMutation,
    error: signUpError,
    isPending: signUpPending,
  } = useMutation({
    mutationFn: (user: UserCreate) => createUser({ body: user }),
    onSuccess: () => {
      console.log('User created successfully');
      navigate({ to: '/login' });
    },
    onError: (error) => {
      console.error('User creation failed:', error);
      if (error?.status === 409 && error?.detail) {
        toast.error(error.detail);
      } else {
        toast.error('Account creation failed.');
      }
    },
  });

  const handleSubmit = (values: typeof form.values) => {
    const { username, password } = values;
    signUpMutation({ username, password });
  };

  const usernameErrors = signUpError?.invalid_params?.filter(
    (param) => param.name === 'username',
  );
  const passwordErrors = signUpError?.invalid_params?.filter(
    (param) => param.name === 'password',
  );

  return (
    <UserForm
      form={form}
      onSubmit={form.onSubmit(handleSubmit)}
      pending={signUpPending}
      submitLabel="Sign Up"
      usernameErrors={usernameErrors}
      passwordErrors={passwordErrors}
      extra={
        <Text mt="md" ta="center" size="sm">
          Already have an account?{' '}
          <Anchor component={Link} to="/login">
            Log in
          </Anchor>
        </Text>
      }
    />
  );
}
