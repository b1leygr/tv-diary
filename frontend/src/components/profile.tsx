import { Avatar, Menu, UnstyledButton } from '@mantine/core';
import { useRouteContext, useRouter } from '@tanstack/react-router';

export function Profile() {
  const { auth, queryClient } = useRouteContext({ from: '__root__' });
  const router = useRouter();

  const handleLogout = () => {
    auth.logout();
    queryClient.clear();
    router.invalidate();
    router.navigate({ to: '/login' });
  };

  const handleActivity = () => {
    router.navigate({ to: '/activity' });
  };

  return (
    <Menu shadow="md" width={200} position="bottom-end">
      <Menu.Target>
        <UnstyledButton
          style={{
            padding: 'var(--mantine-spacing-md)',
            color: 'var(--mantine-color-text)',
            borderRadius: 'var(--mantine-radius-sm)',
          }}
        >
          <Avatar radius="xl" />
        </UnstyledButton>
      </Menu.Target>
      <Menu.Dropdown>
        <Menu.Item component="button" onClick={handleActivity}>
          Activity
        </Menu.Item>
        <Menu.Item component="button" onClick={handleLogout}>
          Log Out
        </Menu.Item>
      </Menu.Dropdown>
    </Menu>
  );
}
