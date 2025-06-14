enum Role {
  admin = "Admin",
  user = "User",
  guest = "Guest"
}

function checkAccess(role: Role): void {
  if (role === Role.admin) {
    console.log("Access granted to admin.");
  } else if (role === Role.user) {
    console.log("Access granted to user.");
  } else if (role === Role.guest) {
    console.log("Access granted to guest.");
  } else {
    console.log("Access denied.");
  }
}

checkAccess(Role.admin);

type pet = "cat" | "dog" | "rabbit";
let myPet: pet = "cat";
// pet = "hello";
// tsc test.ts
// node test.js