import { Container, Flex, type FlexProps } from '@mantine/core';

interface FormFlexProps extends FlexProps {
  formContent: React.ReactNode;
}

export function FormFlex({ formContent, ...props }: FormFlexProps) {
  return (
    <Flex
      justify="center"
      align="center"
      style={{
        height:
          'calc(100vh - var(--app-shell-header-height, 0px) - var(--app-shell-padding) * 2)',
      }}
      {...props}
    >
      <Container size="xl" w="100%" p="md">
        {formContent}
      </Container>
    </Flex>
  );
}
