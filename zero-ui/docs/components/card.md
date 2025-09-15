# Card

Flexible content container component with optional header, content, and footer sections.

## Import

```vue
<script setup lang="ts">
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/shadcn/card'
</script>
```

## Examples

### Basic Card

```vue
<template>
  <Card>
    <CardContent>
      <p>Simple card content</p>
    </CardContent>
  </Card>
</template>
```

### Card with Header

```vue
<template>
  <Card>
    <CardHeader>
      <CardTitle>Card Title</CardTitle>
      <CardDescription>
        Optional description for the card
      </CardDescription>
    </CardHeader>
    <CardContent>
      <p>Main content goes here</p>
    </CardContent>
  </Card>
</template>
```

### Full Card

```vue
<template>
  <Card>
    <CardHeader>
      <CardTitle>Complete Card</CardTitle>
      <CardDescription>
        This card has all sections
      </CardDescription>
    </CardHeader>
    <CardContent>
      <p>Main content section</p>
    </CardContent>
    <CardFooter>
      <Button>Action</Button>
      <Button variant="outline">Cancel</Button>
    </CardFooter>
  </Card>
</template>
```

## Components

### Card
The main container component.

### CardHeader
Contains the title and optional description.

### CardTitle
The main heading for the card.

### CardDescription
Optional subtitle or description text.

### CardContent
The main content area of the card.

### CardFooter
Action area, typically containing buttons.

## Styling

Cards use a consistent spacing and styling system:
- Rounded corners with `rounded-xl`
- Subtle border and shadow
- Consistent internal padding
- Responsive design