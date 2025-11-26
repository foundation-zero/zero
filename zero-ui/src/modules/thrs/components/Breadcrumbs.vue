<script lang="ts" setup>
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { useI18n } from "vue-i18n";

const { t } = useI18n();
</script>

<template>
  <Breadcrumb>
    <BreadcrumbList
      data-testid="breadcrumbs"
      class="text-muted-foreground text-xs"
    >
      <BreadcrumbItem>
        <BreadcrumbLink href="/thrs/overview">{{ t("labels.thrs") }}</BreadcrumbLink>
      </BreadcrumbItem>
      <BreadcrumbSeparator />
      <BreadcrumbItem>
        <BreadcrumbPage href="/thrs/pump-control">{{ t("labels.pumpControl") }}</BreadcrumbPage>
      </BreadcrumbItem>
    </BreadcrumbList>
  </Breadcrumb>
</template>
