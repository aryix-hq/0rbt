# UI/UX Architecture & Design System Engineering Standards

All frontend interfaces, UI components, design tokens, and user interactions authored within this repository must adhere strictly to these architectural standards. Ad-hoc styling, arbitrary pixel values, unprincipled component duplication, and visual inconsistency ("design drift") are strictly forbidden.

---

## 1. Spatial Grid & Coordinate Matrix

- **The 4px/8px Geometric Grid**: All spacing, padding, margins, gutters, component heights, and icon bounding boxes must derive from integer multiples of 4px:
  $$\text{Dimension} \in \{4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 128\}\text{ px}$$
- **Prohibition of Arbitrary Pixel Values**: Arbitrary utility escapes (e.g., Tailwind `top-[13px]`, `w-[317px]`, `p-[19px]`, `gap-[7px]`) are strictly rejected during code review. All layout coordinates must snap to the spatial scale tokens (`space-1` through `space-32`).
- **Layout Alignment**: Use flexbox and CSS grid with explicit alignment (`items-center`, `justify-between`, `gap-*`). Never use magic negative margins or absolute offsets to align sibling elements.

---

## 2. Token Hierarchy & Living Token Contracts

- **Three-Tier Token Architecture**:
  1. **Global Tokens (Primitive)**: Raw color values, fonts, and dimensions (e.g., `--primitive-slate-900: #0f172a;`).
  2. **Semantic Tokens (System)**: Contextual aliases bound to intent (e.g., `--bg-canvas: var(--primitive-slate-900);`, `--text-secondary: var(--primitive-slate-400);`, `--border-subtle: var(--primitive-slate-800);`).
  3. **Component Tokens (Scoped)**: Element-level properties (e.g., `--btn-primary-bg: var(--accent-blue-600);`).
- **No Direct Raw Colors in Components**: UI components must never hardcode hex colors (`#1e293b`) or RGB strings. All components consume semantic CSS variables or standardized design tokens (`DESIGN.md`).
- **Dark Mode First-Class Invariant**: Dark mode is not an afterthought; all token contracts define dark mode defaults with minimum luminance contrast thresholds.

---

## 3. Atomic Design Layering & Boundary Governance

- **Strict Layer Separation**:
  - **Atoms**: Primitive building blocks with zero business logic (Button, Input, Badge, Icon, Avatar, Label).
  - **Molecules**: Combinations of atoms forming functional units (FormField, SearchBar, MetricCard, TabGroup).
  - **Organisms**: Distinct UI sections composed of molecules and atoms (Navbar, DataTable, FilterDrawer, ModalDialog).
  - **Templates / Pages**: Structural view layouts binding organisms to domain state.
- **Dependency Flow**: Higher-level components may import lower-level ones; lower-level components (Atoms/Molecules) must NEVER import or depend on Organisms or Pages.

---

## 4. Component API Contracts & Invariants

All reusable UI components must provide a standardized TypeScript interface contract:

```typescript
export interface BaseComponentProps<T = HTMLElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isDisabled?: boolean;
  isLoading?: boolean;
  className?: string;
  children?: React.ReactNode;
}
```

- **Interactive State Completeness**: Every interactive atom (button, link, input, checkbox, select) must explicitly define and style all five states:
  1. Default
  2. Hover (`:hover`)
  3. Active / Pressed (`:active`)
  4. Focus-Visible (`:focus-visible` with a high-contrast focus ring)
  5. Disabled (`:disabled` / `aria-disabled="true"`)
- **Semantic HTML & Accessibility**: Interactive elements must use native semantic tags (`<button>`, `<a href="...">`, `<input>`) or full ARIA semantics (`role="button"`, `tabIndex={0}`, `onKeyDown`).

---

## 5. Floor, Reflex & Finish Quality Standards

- **WCAG 2.1 AA Contrast**:
  - Regular body text and interactive labels must maintain a contrast ratio $\ge 4.5:1$ against their immediate background.
  - Large headings and essential UI boundaries/icons must maintain $\ge 3.0:1$.
- **The Three States Rule (Floor)**: Every data-driven component or container must explicitly render:
  1. **Loading State**: Content skeleton loader matching layout geometry (not a generic blank spinner).
  2. **Empty / Zero State**: Informative graphic, descriptive copy, and a primary call-to-action to create data.
  3. **Error State**: Non-destructive error message with a retry trigger.
- **Reflex (Interaction Speed)**: Transitions must use standardized timing curves:
  - Micro-interactions (hover, press): $100\text{ms} - 150\text{ms}$ (`ease-out`).
  - Container expansions / drawers: $200\text{ms} - 300\text{ms}$ (`cubic-bezier(0.16, 1, 0.3, 1)`).
  - Animations must respect `prefers-reduced-motion: reduce`.

---

## 6. The 5-Pass Anti-Slop UI De-slopping Protocol

Derived from NeuralDev's *Unslop UI* framework and `skills.rest/skill/anti-vibe-review`, every frontend UI authoring or refactoring task must execute five sequential verification passes before opening a PR:

1. **Pass 1: Spatial Grid & Viewport Resiliency**:
   - Zero horizontal overflow on 375px mobile screens.
   - Minimum 44x44px touch targets on interactive controls.
   - Strict 4px/8px coordinate snapping (`p-2`, `p-4`, `p-6`, `p-8`); zero arbitrary pixel brackets (`p-[19px]`).
2. **Pass 2: Color System & Contrast Discipline**:
   - WCAG 2.1 AA compliant contrast ($\ge 4.5:1$ text, $\ge 3:1$ UI boundaries).
   - Zero gratuitous purple-to-indigo or cyan-to-magenta gradient blobs. Colors must derive strictly from living brand tokens (`Electric Blue #3b82f6`, `Midnight #020617`, `Slate #0f172a`, `Emerald #10b981`).
3. **Pass 3: Authentic Microcopy & Typographic Hierarchy**:
   - Absolute ban on generic AI placeholder copy ("Supercharge", "Unleash", "Next-gen", "All-in-one", "Seamless").
   - Replace with concrete domain metrics and actionable labels.
   - Strict typographic scale: Display $\to$ H1 $\to$ H2 $\to$ Body $\to$ Caption $\to$ Monospace. Tabular numbers (`tabular-nums`) for currency and metrics.
4. **Pass 4: Complete Interactive State Matrix (7-State Standard)**:
   - Verify all 7 states for every interactive component: `Default`, `Hover`, `Focus-Visible`, `Active`, `Disabled`, `Loading (Skeleton)`, and `Empty State`.
5. **Pass 5: Redesign Preservation Gate**:
   - Prohibits dropping functionality during UI re-styling: 100% of event handlers (`onClick`, `onSubmit`, `onChange`), form inputs, hidden CSRF fields, navigation links, and ARIA accessibility labels must remain active and bound.
