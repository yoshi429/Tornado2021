// post_list
const openPostModal = postId => {
  document.getElementById(`post-modal-${postId}`)
    ?.classList.add("open-modal");
  console.log(postId);
};

const closePostModal = postId => {
  document.getElementById(`post-modal-${postId}`)
    ?.classList.remove("open-modal");
  console.log(postId);
};

// newpost
let spotCount = 0;
let editSpotId = null;

const openEditModal = spotId => {
  document.getElementById("new-post-modal-content").classList.add("stucked");
  document.getElementById("spot-edit-modal").classList.add("open-modal");
  if (spotId != null) {
    editSpotId = spotId;
    // 現在の入力内容を取得
    const title = document.querySelector(`#spot-card-${spotCount} .spot-card-title`).value;
    const description = document.querySelector(`#spot-card-${spotCount} .spot-card-description`).value;
    // 入力内容をモーダルに反映
    document.getElementById("spot-title-input").value = title;
    document.getElementById("spot-description-input").value = description;
  }
  // document.getElementById(`added-spot-${spotId}`)
};

const completeEditModal = () => {
  if (spotCount > 5) {
    alert("スポットはこれ以上登録できません");
    return;
  }
  // モーダルの入力内容を取得
  const title = document.getElementById("spot-title-input").value;
  const description = document.getElementById("spot-description-input").value;
  const imgSrc = document.getElementById("spot-edit-modal-img").src;
  if (title == null || title === "") {
    alert("タイトルを入力してください");
    return;
  }
  if (imgSrc == null || imgSrc === "") {
    alert("画像をアップロードしてください");
    return;
  }

  // モーダルを表示
  document.getElementById("new-post-modal-content").classList.remove("stucked");
  document.getElementById("spot-edit-modal").classList.remove("open-modal");

  // モーダルの内容をクリア
  document.getElementById("spot-title-input").value = "";
  document.getElementById("spot-description-input").value = "";

  // 新規追加か判定
  if (editSpotId == null) {
    spotCount += 1;
    // spot-cardを表示
    document.getElementById(`spot-card-${spotCount}`).classList.remove("not-added");
    document.querySelector(`#spot-card-${spotCount} .spot-card-title`).value = title;
    document.querySelector(`#spot-card-${spotCount} .spot-card-description`).value = description;
    document.querySelector(`#spot-card-${spotCount} .spot-img-top`).src = imgSrc;
  } else {
    // spot-cardに反映
    document.querySelector(`#spot-card-${editSpotId} .spot-card-title`).value = title;
    document.querySelector(`#spot-card-${editSpotId} .spot-card-description`).value = description;
    document.querySelector(`#spot-card-${editSpotId} .spot-img-top`).src = imgSrc;
    // 編集終了
    editSpotId = null;
  }
};

// 編集/追加モーダルの画像プレビュー
const onSelectSpotImage = e => {
  if (e.files.length === 0) {
    return;
  }
  const imgUrl = URL.createObjectURL(e.files[0]);
  console.log(imgUrl);
  document.getElementById("spot-edit-modal-img").src = imgUrl;
};

// カテゴリ選択時の反映
const onSelectCategory = category => {
  document.getElementById("plan-category").value = category;
  document.getElementById(`${category}-category-button`).classList.add("selected");
  ["pets", "elderly", "wheelchair"].forEach(_category => {
    if (category === _category) {
      document.getElementById(`${_category}-category-button`).classList.add("selected");
      document.getElementById(`${_category}-category-button`).classList.add("selected");
    } else {
      document.getElementById(`${_category}-category-button`).classList.remove("selected");
      document.getElementById(`${_category}-category-button`).classList.remove("selected");
    }
  });
};

window.onload = () => {
  // 初期値の設定
  onSelectCategory("pets");
};
