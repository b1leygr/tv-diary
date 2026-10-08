import { TextInput } from '@mantine/core';
import { useForm } from '@mantine/form';
import { useNavigate, useRouterState } from '@tanstack/react-router';
import { SearchIcon } from 'lucide-react';
import { useEffect } from 'react';

export function SearchBar() {
  const navigate = useNavigate();
  const location = useRouterState({ select: (s) => s.location });
  const urlParams = new URLSearchParams(location.searchStr);
  const urlQuery = urlParams.get('query') || '';

  const form = useForm({
    mode: 'uncontrolled',
    initialValues: {
      query: urlQuery,
    },
    validate: {
      query: (value) =>
        value.trim().length < 2 ? 'Search query too short' : null,
    },
  });

  useEffect(() => {
    form.setValues({ query: urlQuery });
  }, [urlQuery, form.setValues]);

  const handleSearch = (values: typeof form.values) => {
    navigate({ to: '/search', search: { query: values.query } });
  };

  return (
    <form onSubmit={form.onSubmit(handleSearch)}>
      <TextInput
        placeholder="Search shows..."
        rightSection={<SearchIcon />}
        key={form.key('query')}
        {...form.getInputProps('query')}
      />
    </form>
  );
}
