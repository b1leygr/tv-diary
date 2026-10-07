import {
  Button,
  Container,
  Paper,
  PasswordInput,
  TextInput,
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from '@tanstack/react-router';
import { createUser, type UserCreate } from '#/client';

export function SignupForm() {
  const form = useForm({
    initialValues: {
      username: '',
      password: '',
    },
  });
  const navigate = useNavigate();

  const signUpMutation = useMutation({
    mutationFn: (user: UserCreate) => createUser({ body: user }),
    onSuccess: () => {
      console.log('User created successfully');
      navigate({ to: '/login' });
    },
    onError: (error) => {
      console.error('User creation failed:', error);
    },
  });

  const handleSubmit = (values: typeof form.values) => {
    const { username, password } = values;
    signUpMutation.mutate({ username, password });
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
            mt="xl"
            loading={signUpMutation.isPending}
          >
            Create Account
          </Button>
        </form>
      </Paper>
    </Container>
  );
}
