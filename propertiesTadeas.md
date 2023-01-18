# Properties For Timelock Authorizer

```ruby
- `defState1` - (Non created/Closed) is defined as `auctions[id].end_time` is 0.
- `defState2` - (Created/Started) is defined as `auctions[id].end_time` is not 0.
```

***Valid state*** - 


***Variable transition*** -


***Variable transition*** - 

***Variable transition*** - 

***High-level*** - Only executor can call these functions:
 - setPendingRoot

***High-level*** - When `scheduleRootChange` is called and `msg.sender` is not root, then `_pendingRoot`, `_root` remain the same and there is no new scheduled event.

***High-level*** - Solvency - Total supply of tokens is greater or equal to the sum of balances of all users. The system has enough tokens to pay everyone what the deserve.

***Unit tests*** -
***Unit tests*** - 

</br>

---

## Prioritizing

</br>

Once the list of properties is finished, the team meet to discuss it. Each property is explained by its creator to the others, and either being approved, denied or refined.
With every property the team discuss the implications of the property failing, and prioritize them accordingly.

Here is a summary of our prioritization:

### High Priority:

- Property 1 is high priority because user can win the auction and get benefits only once by initial intention. Moreover, `mint()` increases a value of `totalSupply` that can block other auctions to finish if you can claim prize multiple times.

- Properties 2 & 5 are high priority because if they fail the winner will not get his/her deserved reward which fails the entire idea of this system.

- Property 3 is high priority because `mint()` increases a value of `totalSupply` that can block other auctions to finish if you can claim huge prize. Also we want to prevent attacker from getting additional benefits.

- Properties 4 & 7 are high priority because violation of this rule means that attacker can unjustly win an auction without any competition (kind of DoS).

- Property 6 is high priority because we want to prevent DoS attack. Otherwise, there is no reason to participate in such auction.

### Medium Priority:

- Property 8 is medium priority only because there is no withdraw method that could decrease totalSupply to 0 and prevent people from getting their tokens. Otherwise, it's high priority.

### Low Priority:

- Properties 9 & 10 are low priority since:
    1. They check implementation of a specific function (as oppose to multiple functions).
    2. They fairly simple to check by other means, including by manual reviewing of the code.