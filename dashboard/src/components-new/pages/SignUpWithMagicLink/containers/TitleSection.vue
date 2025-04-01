<template>
  <div>
    <h1 class="text-2xl font-bold">新規会員登録</h1>
    <div
      class="flex flex-col gap-4 p-6 my-4 border-2 border-gray-200 rounded-md"
    >
      <div>
        <p class="text-sm">
          当サイトへの会員登録申請は、法人・事業者のお客様限定となります。
        </p>
        <p class="text-sm">一般消費者の方の登録はお受けしておりません。</p>
      </div>
      <div>
        <p class="text-sm">
          <RequiredBadge />
          <span> は必須入力項目です。</span>
        </p>
        <p class="text-sm">
          「ご利用規約」を必ずお読みいただき、同意いただける場合は【規約に同意する】にチェックを入れ、
        </p>
        <p class="text-sm">【登録する】ボタンを押して登録してください。</p>
      </div>
      <div>
        <p class="text-sm">パスワードは、以下の規則に従ってください。</p>
        <ul class="list-disc pl-5 text-sm">
          <li>12文字以上かつ16文字以下</li>
          <li>
            半角の英字(大文字)、英字(小文字)、数字、記号それぞれすべてを最低1文字以上含む
          </li>
          <li>
            入力可能な記号のリスト:
            <code class="bg-blue-100 text-blue-500 p-1 text-sm rounded">
              @ # $ % ^ &amp; * - _ + = [ ] { } | \ : ' , ? / ` ~ " ( ) ;
            </code>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import RequiredBadge from '../presenters/RequiredBadge.vue';
</script>
