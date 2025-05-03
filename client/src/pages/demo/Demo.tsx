import * as React from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuCheckboxItem,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu';
import {
  Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardDescription,
  CardContent,
} from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectSeparator,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Star } from 'lucide-react';
import { motion } from 'framer-motion';

/**
 * Demo page for all UI components and their variants.
 * --------------------------------------------------
 * - Shows Card, Input, Button, Select, and DropdownMenu in all variants.
 */
function Demo() {
  // State for dropdown checkbox and radio demo
  const [checked, setChecked] = React.useState(true);
  const [radio, setRadio] = React.useState('option-1');
  // State for select demo
  const [selectValue, setSelectValue] = React.useState('option-1');

  return (
    <motion.div
      className="_Demo max-w-2xl mx-auto py-12 h-[100vh]"
      key="demo"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.8 }}
    >
      <div className="text-center mb-12">
        <h1 className="text-2xl font-bold tracking-tight sm:text-4xl mb-4">Components Demo</h1>
        <p className="text-gold-700">
          All variants of Card, Input, Button, Select, and DropdownMenu
        </p>
      </div>

      <div className="flex flex-col gap-8">
        <section>
          <h2 className="text-lg font-semibold mb-4 text-gold-700">Card Demo</h2>
          <div className="space-y-8">
            <Card>
              <CardHeader>
                <CardTitle>Gold Themed Card</CardTitle>
                <CardDescription>
                  This card uses the gold theme for background, border, and shadow. The title uses
                  gold text.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p>
                  This is the card content. You can put any content here, such as text, forms, or
                  other components.
                </p>
              </CardContent>
              <CardFooter>
                <Button>Card Action</Button>
              </CardFooter>
            </Card>
          </div>
        </section>

        <section>
          <h2 className="text-lg font-semibold mb-4 text-gold-700">Input Variants</h2>
          <div className="space-y-4">
            {/* Default input */}
            <Input placeholder="Default input" />
            {/* Disabled input */}
            <Input placeholder="Disabled input" disabled />
            {/* Input with value */}
            <Input defaultValue="With value" />
          </div>
        </section>

        <section>
          <h2 className="text-lg font-semibold mb-4 text-gold-700">Button Variants</h2>
          <div className="flex flex-wrap gap-4 mb-6">
            {/* Default */}
            <Button>Default</Button>
            {/* Outline */}
            <Button variant="outline">Outline</Button>
            {/* Secondary */}
            <Button variant="secondary">Secondary</Button>
            {/* Ghost */}
            <Button variant="ghost">Ghost</Button>
            {/* Link */}
            <Button variant="link">Link</Button>
            {/* Destructive */}
            <Button variant="destructive">Destructive</Button>
          </div>
          <div className="flex flex-wrap gap-4 items-center">
            {/* Sizes */}
            <Button size="sm">Small</Button>
            <Button size="default">Default</Button>
            <Button size="lg">Large</Button>
            <Button size="icon" aria-label="icon only">
              <Star className="size-5" />
            </Button>
          </div>
        </section>

        <section>
          <h2 className="text-lg font-semibold mb-4 text-gold-700">Select Demo</h2>
          <div className="space-y-4">
            <label className="block text-gold-700 font-medium mb-2">Gold Themed Select</label>
            <Select value={selectValue} onValueChange={setSelectValue}>
              <SelectTrigger className="min-w-[200px]">
                <SelectValue placeholder="Select an option" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectLabel>Options</SelectLabel>
                  <SelectItem value="option-1">Option 1</SelectItem>
                  <SelectItem value="option-2">Option 2</SelectItem>
                  <SelectItem value="option-3">Option 3</SelectItem>
                  <SelectSeparator />
                  <SelectItem value="disabled" disabled>
                    Disabled Option
                  </SelectItem>
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>
        </section>

        <section>
          <h2 className="text-lg font-semibold mb-4 text-gold-700">Dropdown Menu Variants</h2>
          <div className="flex gap-8">
            {/* Default DropdownMenu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button className="px-8 py-1">Open Menu</Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuLabel>Menu</DropdownMenuLabel>
                <DropdownMenuItem>Default Item</DropdownMenuItem>
                <DropdownMenuItem inset>Inset Item</DropdownMenuItem>
                <DropdownMenuItem variant="destructive">Destructive Item</DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuCheckboxItem checked={checked} onCheckedChange={setChecked}>
                  Checkbox Item
                </DropdownMenuCheckboxItem>
                <DropdownMenuSeparator />
                <DropdownMenuRadioGroup value={radio} onValueChange={setRadio}>
                  <DropdownMenuRadioItem value="option-1">Radio 1</DropdownMenuRadioItem>
                  <DropdownMenuRadioItem value="option-2">Radio 2</DropdownMenuRadioItem>
                </DropdownMenuRadioGroup>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </section>
      </div>
    </motion.div>
  );
}

export default Demo;
